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
            return st.secrets.get(key, default)
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
# Use lazy evaluation to avoid accessing st.secrets before st.set_page_config()
def _get_groq_api_key():
    """Get GROQ_API_KEY with proper priority (lazy evaluation)."""
    return _get_from_streamlit_secrets("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY", "")

GROQ_API_KEY = _get_groq_api_key()
if not GROQ_API_KEY:
    import warnings
    warnings.warn(
        "GROQ_API_KEY not set! Set it via Streamlit secrets, environment variable, or .env file. "
        "LLM features will not work without it.",
        UserWarning
    )

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
