import pytesseract
from subprocess import run
from config import TESSERACT_PATH, POPPLER_PATH

print("Testing Tesseract...")
print(TESSERACT_PATH)
run([TESSERACT_PATH, "--version"])

print("\nTesting Poppler...")
print(POPPLER_PATH)
run([f"{POPPLER_PATH}\\pdftoppm.exe", "-v"])
