from groq import Groq
from config import get_groq_api_key

# Get API key at runtime
api_key = get_groq_api_key()
if not api_key:
    raise ValueError("GROQ_API_KEY not configured. Set it via Streamlit secrets, environment variable, or .env file.")

client = Groq(api_key=api_key)

resp = client.models.list()

print("\nAvailable Groq Models:\n")
for m in resp.data:
    print(m.id)
