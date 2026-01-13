# Streamlit Secrets Setup - Quick Reference

## How to Add Secrets in Streamlit Cloud

### Step 1: Access Secrets
1. Go to https://share.streamlit.io/
2. Select your app
3. Click **"⚙️ Settings"** → **"Secrets"**

### Step 2: Add Your API Key

Click **"Edit secrets"** and paste this format:

```toml
[secrets]
GROQ_API_KEY = "your_actual_groq_api_key_here"
```

### Step 3: Example

If your Groq API key is `gsk_abc123xyz789`, your secrets file should look like:

```toml
[secrets]
GROQ_API_KEY = "gsk_abc123xyz789"
```

### Step 4: Save and Redeploy

1. Click **"Save"**
2. Go back to your app
3. Click **"Redeploy"** (or it will auto-redeploy)

### ✅ Done!

Your app will now have access to the API key securely.

---

## Important Notes

- 🔒 Secrets are encrypted and never exposed in code or logs
- ✅ No need to create `.env` file on Streamlit Cloud
- ✅ Secrets take priority over environment variables
- ❌ Never put secrets in your code or GitHub

---

## Troubleshooting

**Problem:** "GROQ_API_KEY not configured"

**Solution:**
1. Check secrets are saved correctly
2. Make sure format is exactly: `GROQ_API_KEY = "key_here"` (with quotes)
3. Redeploy after saving secrets
4. Check logs for any errors

---

For full deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

