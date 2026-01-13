"""
OCR module for extracting text from PDFs and images.

Requires:
- Tesseract OCR installed and accessible
- Poppler (for PDF processing)
"""
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from config import TESSERACT_PATH, POPPLER_PATH
from pathlib import Path

# Configure Tesseract path
# Set the path early so pytesseract can use it
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


class OCRError(Exception):
    """Raised when OCR operations fail."""
    pass


def _check_tesseract():
    """Verify Tesseract is available."""
    import os
    
    # Check if we're on Streamlit Cloud (where OCR isn't available)
    if os.environ.get("STREAMLIT_SERVER_ENVIRONMENT") == "cloud":
        raise OCRError(
            "OCR is not available on Streamlit Cloud. "
            "Tesseract and Poppler require local installation. "
            "Please use OCR features in local development only."
        )
    
    # Ensure pytesseract is configured with the correct path
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    
    # Check if Tesseract exists - try multiple methods for Windows compatibility
    path_exists = False
    actual_path = None
    
    # Method 1: os.path.exists() (most reliable on Windows with spaces)
    if os.path.exists(TESSERACT_PATH):
        path_exists = True
        actual_path = TESSERACT_PATH
    # Method 2: Path.exists() (standard)
    else:
        tesseract_path = Path(TESSERACT_PATH)
        if tesseract_path.exists():
            path_exists = True
            actual_path = str(tesseract_path)
        # Method 3: Try to resolve the path
        else:
            try:
                resolved = tesseract_path.resolve()
                if resolved.exists():
                    path_exists = True
                    actual_path = str(resolved)
            except Exception:
                pass
    
    if not path_exists:
        raise OCRError(
            f"Tesseract not found at: {TESSERACT_PATH}\n"
            f"Please verify the path is correct.\n"
            f"Common locations:\n"
            f"  - C:\\Program Files\\Tesseract-OCR\\tesseract.exe\n"
            f"  - C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe\n"
            f"You can also set TESSERACT_PATH in your .env file."
        )
    
    # Update pytesseract with the actual resolved path if different
    if actual_path and actual_path != TESSERACT_PATH:
        pytesseract.pytesseract.tesseract_cmd = actual_path
    
    # Verify Tesseract is actually executable (optional check)
    try:
        import subprocess
        test_path = actual_path or TESSERACT_PATH
        result = subprocess.run(
            [test_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        if result.returncode != 0:
            # Don't fail here, just log - the file exists so we'll try it
            pass
    except Exception:
        # If subprocess fails, continue anyway - file exists
        pass


def image_to_text(image: Image.Image) -> str:
    """
    Extract text from a PIL Image using Tesseract OCR.
    
    Args:
        image: PIL Image object
        
    Returns:
        Extracted text string
        
    Raises:
        OCRError: If OCR fails
    """
    _check_tesseract()
    try:
        text = pytesseract.image_to_string(image)
        return text.strip() if text else ""
    except Exception as e:
        raise OCRError(f"Failed to extract text from image: {e}")


def pdf_to_text(pdf_path: str, dpi: int = 300) -> str:
    """
    Extract text from a PDF file using OCR.
    
    Args:
        pdf_path: Path to the PDF file
        dpi: Resolution for PDF to image conversion (higher = better quality but slower)
        
    Returns:
        Extracted text from all pages
        
    Raises:
        OCRError: If PDF conversion or OCR fails
    """
    _check_tesseract()
    
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise OCRError(f"PDF file not found: {pdf_path}")
    
    # Check Poppler
    import os
    poppler_path = Path(POPPLER_PATH)
    poppler_exists = poppler_path.exists() or os.path.exists(POPPLER_PATH)
    
    if not poppler_exists:
        raise OCRError(
            f"Poppler not found at: {POPPLER_PATH}\n"
            "Install Poppler and update POPPLER_PATH in config.py or .env\n"
            "Download from: https://github.com/oschwartz10612/poppler-windows/releases"
        )
    
    try:
        pages = convert_from_path(pdf_path, dpi, poppler_path=POPPLER_PATH)
    except Exception as e:
        raise OCRError(f"Failed to convert PDF to images: {e}")
    
    if not pages:
        return ""
    
    full_text = []
    for i, page in enumerate(pages):
        try:
            page_text = pytesseract.image_to_string(page)
            if page_text:
                full_text.append(page_text.strip())
        except Exception as e:
            full_text.append(f"[Error on page {i+1}: {e}]")
    
    return "\n\n".join(full_text)
