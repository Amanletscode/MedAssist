# MedAssist AI - Deployment Guide

This guide will walk you through deploying MedAssist AI to Streamlit Cloud step by step.

---

## 📋 Prerequisites

Before starting, make sure you have:
- ✅ A GitHub account (free)
- ✅ A Streamlit Cloud account (free at https://streamlit.io/cloud)
- ✅ A Groq API key (free at https://console.groq.com/)
- ✅ Git installed on your computer

---

## 🚀 Step-by-Step Deployment

### **Step 1: Prepare Your Code**

#### 1.1 Verify Your Files
Make sure these files exist and are correct:
- ✅ `streamlit_app.py` - Your main Streamlit app
- ✅ `requirements.txt` - All dependencies
- ✅ `.gitignore` - Prevents committing secrets
- ✅ `.env.example` - Template for environment variables

#### 1.2 Check Your .gitignore
Your `.gitignore` should include:
```
.env
*.env
__pycache__/
venv/
*.npy
```

**Important:** Never commit your `.env` file or actual API keys!

---

### **Step 2: Push to GitHub**

#### 2.1 Initialize Git Repository (if not already done)

Open PowerShell or Command Prompt in your project folder and run:

```powershell
# Check if git is initialized
git status

# If not initialized, run:
git init
```

#### 2.2 Create a .gitignore (if needed)

If you don't have a `.gitignore`, create one with the content shown in Step 1.2.

#### 2.3 Stage Your Files

```powershell
# Add all files (except those in .gitignore)
git add .

# Check what will be committed (make sure .env is NOT listed!)
git status
```

**⚠️ CRITICAL:** Verify that `.env` is NOT in the list of files to be committed!

#### 2.4 Commit Your Code

```powershell
git commit -m "Initial commit: MedAssist AI app"
```

#### 2.5 Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `medassist-ai` (or any name you prefer)
3. Description: "AI-powered medical coding assistant"
4. Choose **Public** or **Private** (both work with Streamlit Cloud)
5. **DO NOT** check "Initialize with README" (you already have files)
6. Click **"Create repository"**

#### 2.6 Push to GitHub

GitHub will show you commands. Use these (replace `YOUR_USERNAME` with your GitHub username):

```powershell
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/medassist-ai.git

# Rename your main branch to 'main' (if needed)
git branch -M main

# Push your code
git push -u origin main
```

You'll be prompted for your GitHub username and password (or personal access token).

**✅ Success:** Your code is now on GitHub!

---

### **Step 3: Deploy on Streamlit Cloud**

#### 3.1 Sign Up / Log In to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click **"Sign up"** or **"Log in"**
3. Sign in with your GitHub account (recommended)

#### 3.2 Create New App

1. Click **"New app"** button
2. You'll see a form to configure your app:
   - **Repository:** Select your `medassist-ai` repository
   - **Branch:** Select `main` (or `master` if that's your branch)
   - **Main file path:** Enter `streamlit_app.py`
   - **App URL:** Choose a custom URL (e.g., `medassist-ai`)

3. **DO NOT click "Deploy!" yet** - we need to add secrets first!

#### 3.3 Add Your API Key as Secret

**Before deploying, add your secrets:**

1. In the Streamlit Cloud dashboard, click on your app (or go to app settings)
2. Click **"⚙️ Settings"** or **"Secrets"** tab
3. Click **"Edit secrets"** or **"New secret"**
4. You'll see a text editor. Add this format:

```toml
[secrets]
GROQ_API_KEY = "your_actual_groq_api_key_here"
```

**Example:**
```toml
[secrets]
GROQ_API_KEY = "gsk_1234567890abcdefghijklmnopqrstuvwxyz"
```

5. Click **"Save"**

**🔒 Security Note:** Streamlit Cloud encrypts and securely stores your secrets. They are never exposed in your code or logs.

#### 3.4 Deploy Your App

1. Go back to your app settings
2. Click **"Deploy!"** or **"Redeploy"**
3. Streamlit will:
   - Install dependencies from `requirements.txt`
   - Run your `streamlit_app.py`
   - Make your app live!

4. Wait 1-2 minutes for deployment to complete
5. You'll see a **"View app"** button - click it to see your live app!

---

### **Step 4: Verify Deployment**

#### 4.1 Test Your App

1. Open your app URL (e.g., `https://medassist-ai.streamlit.app`)
2. Test the **Chat** feature - it should work with your Groq API key
3. Test **Code Suggestion** - should work without API key
4. **Upload & OCR** - Will show a warning that OCR is not available on Streamlit Cloud (this is expected)

#### 4.2 Check Logs (if issues)

1. In Streamlit Cloud dashboard, click **"Manage app"**
2. Click **"Logs"** tab to see any errors
3. Common issues:
   - Missing dependencies → Check `requirements.txt`
   - API key errors → Verify secrets are set correctly
   - Import errors → Check file paths

---

## 🔧 Troubleshooting

### Issue: "GROQ_API_KEY not configured"

**Solution:**
1. Go to Streamlit Cloud → Your App → Settings → Secrets
2. Verify the secret is formatted correctly:
   ```toml
   [secrets]
   GROQ_API_KEY = "your_key_here"
   ```
3. Make sure there are no extra quotes or spaces
4. Click "Redeploy" after saving

### Issue: "Module not found"

**Solution:**
1. Check `requirements.txt` includes all dependencies
2. Make sure version numbers are correct
3. Redeploy the app

### Issue: "OCR failed" on Streamlit Cloud

**Expected:** OCR requires local installation of Tesseract and Poppler. It's disabled on Streamlit Cloud. This is normal - use OCR features locally only.

### Issue: Deployment fails

**Solution:**
1. Check the Logs tab in Streamlit Cloud
2. Verify `streamlit_app.py` is the correct main file
3. Make sure all imports are correct
4. Check that `requirements.txt` has all packages

---

## 📝 Local Development Setup

For local development (with OCR support):

### 1. Create `.env` file

Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

### 2. Edit `.env` file

Open `.env` and add your actual API key:
```
GROQ_API_KEY=your_actual_groq_api_key_here
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
POPPLER_PATH=C:\path\to\poppler\bin
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run locally

```powershell
streamlit run streamlit_app.py
```

---

## 🔐 Security Best Practices

✅ **DO:**
- Use Streamlit secrets for production
- Keep `.env` in `.gitignore`
- Never commit API keys
- Use `.env.example` as a template

❌ **DON'T:**
- Commit `.env` files
- Hardcode API keys in code
- Share your API keys publicly
- Use production keys in development

---

## 📚 Additional Resources

- **Streamlit Cloud Docs:** https://docs.streamlit.io/streamlit-community-cloud
- **Streamlit Secrets:** https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management
- **Groq API:** https://console.groq.com/
- **GitHub Docs:** https://docs.github.com/

---

## ✅ Deployment Checklist

Before deploying, verify:

- [ ] `.env` is in `.gitignore`
- [ ] `.env.example` exists (without real keys)
- [ ] `requirements.txt` has all dependencies
- [ ] Code is pushed to GitHub
- [ ] Streamlit Cloud secrets are configured
- [ ] App deploys successfully
- [ ] Chat feature works (tests API key)
- [ ] Code suggestion works

---

## 🎉 You're Done!

Your MedAssist AI app is now live on Streamlit Cloud! 

**Your app URL will be:** `https://YOUR-APP-NAME.streamlit.app`

Share it with others and enjoy your deployed AI medical coding assistant!

---

**Need Help?** Check the logs in Streamlit Cloud dashboard or review the troubleshooting section above.

