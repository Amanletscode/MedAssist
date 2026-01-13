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

# Try to load Streamlit secrets (for Streamlit Cloud)
try:
    import streamlit as st
    _streamlit_available = True
except ImportError:
    _streamlit_available = False

def _get_from_streamlit_secrets(key: str, default: str = "") -> str:
    """Get value from Streamlit secrets if available."""
    if _streamlit_available:
        try:
            return st.secrets.get(key, default)
        except Exception:
            # Streamlit secrets not configured or key doesn't exist
            return default
    return default

# Load .env file if it exists (for local development)
# Only load if not using Streamlit secrets (to avoid conflicts)
_env_path = Path(__file__).parent / ".env"
if _env_path.exists() and not _get_from_streamlit_secrets("GROQ_API_KEY"):
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
GROQ_API_KEY = _get_from_streamlit_secrets("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY", "")
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
