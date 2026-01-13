import os
from dotenv import load_dotenv
from config import GROQ_API_KEY

load_dotenv()

# Handle API keys (priority: Streamlit secrets > env var > config.py)
# This ensures Streamlit Cloud secrets take precedence
# Use lazy evaluation to avoid accessing st.secrets before Streamlit is initialized
def _get_api_key():
    """Get API key with proper priority (lazy evaluation)."""
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            return st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY") or GROQ_API_KEY
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY") or GROQ_API_KEY

API_KEY = _get_api_key()

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
                    "GROQ_API_KEY not configured. "
                    "Set it via environment variable or .env file."
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
