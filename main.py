from ocr import pdf_to_text
from llm import LLMClient, LLMError

llm = LLMClient()

def analyze_document(path):
    try:
        text = pdf_to_text(path)
        
        if not text or text.startswith("Error"):
            print(f"OCR Error: {text}")
            return

        messages = [
            {"role": "system", "content": "You are a clinical summarizer."},
            {"role": "user", "content": f"Extract medical information and summarize:\n\n{text}"}
        ]

        print(llm.ask(messages))
    except LLMError as e:
        print(f"LLM Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyze_document(sys.argv[1])
    else:
        print("Usage: python main.py <pdf_path>")
