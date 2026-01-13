import os
from dotenv import load_dotenv

load_dotenv()

# Simple, guaranteed working approach for API key loading
# IMPORTANT: Don't call this at import time - call it when actually needed
def get_groq_key():
    """Get GROQ API key - Streamlit secrets first, then environment variable."""
    # Try Streamlit secrets first (for Streamlit Cloud)
    # This MUST be called at runtime, not import time
    try:
        import streamlit as st
        # Direct access - this works on Streamlit Cloud at runtime
        return st.secrets["GROQ_API_KEY"]
    except (KeyError, AttributeError, Exception):
        # Fall back to environment variable (from .env file or system env)
        return os.getenv("GROQ_API_KEY", "")

# Don't evaluate at import time - will be called when LLM client is used
API_KEY = None

# Best Groq Model
DEFAULT_MODEL = "llama-3.3-70b-versatile"


class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    pass


class LLMClient:
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model = model_name
        self._client = None
        
    @property
    def client(self):
        """Lazy initialization of Groq client."""
        if self._client is None:
            # Get API key at runtime (not import time) - this ensures Streamlit secrets are available
            api_key = get_groq_key()
            if not api_key:
                raise LLMError(
                    "GROQ_API_KEY missing. Add it in Streamlit secrets or set as environment variable."
                )
            try:
                from groq import Groq
                self._client = Groq(api_key=api_key)
            except ImportError:
                raise LLMError("groq package not installed. Run: pip install groq")
        return self._client

    def ask(self, messages: list, max_retries: int = 2) -> str:
        """
        Send messages to the LLM and get a response.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            max_retries: Number of retry attempts on transient errors
            
        Returns:
            The assistant's response text
            
        Raises:
            LLMError: On configuration or API errors
        """
        if not messages:
            raise LLMError("No messages provided")
        
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.2,
                    max_tokens=800,
                )
                return response.choices[0].message.content
                
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Don't retry on auth errors
                if "auth" in error_str or "api_key" in error_str or "unauthorized" in error_str:
                    raise LLMError(f"Authentication failed: {e}")
                
                # Don't retry on rate limits (let caller handle backoff)
                if "rate" in error_str and "limit" in error_str:
                    raise LLMError(f"Rate limit exceeded: {e}")
                
                # Retry on transient errors
                if attempt < max_retries:
                    continue
                    
        raise LLMError(f"LLM request failed after {max_retries + 1} attempts: {last_error}")
