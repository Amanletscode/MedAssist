from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

resp = client.models.list()

print("\nAvailable Groq Models:\n")
for m in resp.data:
    print(m.id)
