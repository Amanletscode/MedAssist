import os
from dotenv import load_dotenv

load_dotenv()

# Simple, guaranteed working approach for API key loading
def get_groq_key():
    """Get GROQ API key - Streamlit secrets first, then environment variable."""
    # Try Streamlit secrets first (for Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except (KeyError, AttributeError, Exception):
        pass
    
    # Fall back to environment variable (from .env file or system env)
    return os.getenv("GROQ_API_KEY", "")

API_KEY = get_groq_key()

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
            if not API_KEY:
                raise LLMError(
                    "GROQ_API_KEY missing. Add it in Streamlit secrets or set as environment variable."
                )
            try:
                from groq import Groq
                self._client = Groq(api_key=API_KEY)
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
