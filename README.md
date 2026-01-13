# MedAssist AI

AI-powered medical coding assistant for healthcare professionals.

## Features

- 🤖 **AI Chat**: Interactive chat with medical AI assistant
- 📄 **Document Processing**: Extract text from scanned documents (local only)
- 🔍 **Code Search**: Find ICD-10 and CPT-4 codes using semantic search
- 📋 **Claim Generation**: Create PDF claim summaries

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/medassist-ai.git
   cd medassist-ai
   ```

2. **Create `.env` file**
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   streamlit run streamlit_app.py
   ```

### Deployment

📖 **See [DEPLOYMENT.md](DEPLOYMENT.md) for complete step-by-step deployment guide to Streamlit Cloud.**

Quick steps:
1. Push code to GitHub
2. Deploy on Streamlit Cloud
3. Add `GROQ_API_KEY` in Streamlit secrets
4. Done! 🎉

## Configuration

### Environment Variables

- `GROQ_API_KEY` (Required): Your Groq API key from https://console.groq.com/
- `TESSERACT_PATH` (Optional): Path to Tesseract OCR (local only)
- `POPPLER_PATH` (Optional): Path to Poppler (local only)

### Streamlit Secrets (for Cloud Deployment)

Add to Streamlit Cloud secrets:
```toml
[secrets]
GROQ_API_KEY = "your_groq_api_key_here"
```

## Technology Stack

- **Frontend**: Streamlit
- **LLM**: Groq (Llama 3.3 70B)
- **Embeddings**: Bio_ClinicalBERT
- **Search**: Semantic + Fuzzy hybrid

## Security

- ✅ Never commit `.env` files
- ✅ Use Streamlit secrets for production
- ✅ Keep API keys secure

## License

This is a portfolio demonstration project.

