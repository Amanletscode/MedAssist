import os
from dotenv import load_dotenv
from config import get_groq_api_key

load_dotenv()

# Handle API keys (priority: Streamlit secrets > env var > config.py)
# This ensures Streamlit Cloud secrets take precedence
# Use lazy evaluation - access secrets at runtime, not import time
def _get_api_key():
    """Get API key with proper priority (lazy evaluation at runtime)."""
    # Priority 1: Streamlit secrets (for Streamlit Cloud)
    try:
        import streamlit as st
        # Try to access secrets - this works at runtime after Streamlit is initialized
        try:
            # Method 1: Try direct access
            if hasattr(st, 'secrets') and st.secrets:
                secret_value = st.secrets.get("GROQ_API_KEY", "")
                if secret_value:
                    return secret_value
        except (AttributeError, RuntimeError, KeyError, Exception) as e:
            # Secrets not available or key doesn't exist
            pass
    except (ImportError, Exception):
        # Streamlit not available
        pass
    
    # Priority 2: Environment variable
    env_value = os.environ.get("GROQ_API_KEY", "")
    if env_value:
        return env_value
    
    # Priority 3: Config fallback
    return get_groq_api_key()

# Don't evaluate at import time - will be set when actually needed
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
            # Get API key at runtime (not import time) to access Streamlit secrets
            api_key = _get_api_key()
            if not api_key:
                raise LLMError(
                    "GROQ_API_KEY not configured. "
                    "Set it via Streamlit secrets, environment variable, or .env file."
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
