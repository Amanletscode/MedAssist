"""
Configuration settings for MedAssist AI.

IMPORTANT: Never commit API keys to version control!
Priority order for configuration:
1. Streamlit secrets (for Streamlit Cloud deployment)
2. Environment variables
3. .env file (for local development)
"""
import os
from pathlib import Path

# Cache for Streamlit availability check
_streamlit_available = None

def _is_streamlit_available():
    """Check if Streamlit is available (lazy check)."""
    global _streamlit_available
    if _streamlit_available is None:
        try:
            import streamlit as st
            _streamlit_available = True
        except ImportError:
            _streamlit_available = False
    return _streamlit_available

def _get_from_streamlit_secrets(key: str, default: str = "") -> str:
    """Get value from Streamlit secrets if available (lazy access)."""
    if not _is_streamlit_available():
        return default
    try:
        import streamlit as st
        # Check if Streamlit runtime is available and initialized
        # This avoids errors if called before st.set_page_config()
        if hasattr(st, 'secrets'):
            # Try dictionary-style access (preferred)
            try:
                if key in st.secrets:
                    value = st.secrets[key]
                    return str(value).strip() if value else default
            except (KeyError, TypeError):
                pass
            # Try attribute-style access as fallback
            try:
                if hasattr(st.secrets, key):
                    value = getattr(st.secrets, key)
                    return str(value).strip() if value else default
            except (AttributeError, TypeError):
                pass
        return default
    except (AttributeError, RuntimeError, Exception):
        # Streamlit not initialized yet, or secrets not configured, or key doesn't exist
        return default

# Load .env file if it exists (for local development)
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_path)
    except ImportError:
        # Fallback to manual parsing if python-dotenv not available
        with open(_env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

# API Keys - Priority: Streamlit secrets > env vars > .env file
# Use lazy evaluation - don't access secrets at import time
def get_groq_api_key():
    """Get GROQ_API_KEY with proper priority (lazy evaluation at runtime)."""
    # Try Streamlit secrets first (only works at runtime, not import time)
    secret_value = _get_from_streamlit_secrets("GROQ_API_KEY")
    if secret_value:
        return secret_value
    # Fall back to environment variable
    return os.environ.get("GROQ_API_KEY", "")

# For backward compatibility, but this will be empty at import time
# The actual key should be retrieved via get_groq_api_key() at runtime
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# External tool paths - Update these for your system or set via environment
# Note: These are only needed for local development. Streamlit Cloud doesn't support OCR.
# Priority: Streamlit secrets > env vars > default paths
TESSERACT_PATH = (
    _get_from_streamlit_secrets("TESSERACT_PATH") or 
    os.environ.get("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
)
POPPLER_PATH = (
    _get_from_streamlit_secrets("POPPLER_PATH") or 
    os.environ.get("POPPLER_PATH", r"C:\Users\amant\poppler-25.12.0\Library\bin")
)
