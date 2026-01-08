# Test Case Generator - Streamlit Web App

Convert your desktop app to a web application! 🎉

## 🚀 Quick Start

### Local Development

1. **Install Streamlit dependencies:**
   ```bash
   pip install -r requirements-streamlit.txt
   ```

2. **Run the app:**
   ```bash
   streamlit run app/streamlit_app.py
   ```

3. **Open in browser:**
   - Streamlit will automatically open at `http://localhost:8501`

### Testing Locally

- Make sure Azure CLI is installed: `az --version`
- Log in to Azure: `az login`
- Enter your API keys in the sidebar
- Generate test cases!

---

## ☁️ Deploy to Streamlit Cloud (FREE)

### Step 1: Push to GitHub

1. **Create a new GitHub repository**
2. **Push your code:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/testcase-generator.git
   git push -u origin main
   ```

### Step 2: Deploy on Streamlit Cloud

1. **Go to:** [share.streamlit.io](https://share.streamlit.io)
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Configure:**
   - Repository: `YOUR-USERNAME/testcase-generator`
   - Branch: `main`
   - Main file path: `app/streamlit_app.py`
5. **Click "Deploy"**

### Step 3: Configure Secrets (Important!)

In Streamlit Cloud app settings, add your secrets:

```toml
[azure]
organization_url = "https://dev.azure.com/your-org"

[github]
token = "ghp_your_github_token"

[openai]
api_key = "sk-your-openai-key"
```

**Note:** Users will still need to authenticate with Azure CLI for their own DevOps access.

---

## 🔧 How It Works

### Web App Features

✅ **Responsive web interface** - Works on any device
✅ **Real-time generation** - See progress as it happens
✅ **Preview & download** - View test cases before downloading
✅ **Activity logging** - Track all operations
✅ **Secure API keys** - Stored safely in Streamlit secrets

### What's Different from Desktop?

| Feature | Desktop (tkinter) | Web (Streamlit) |
|---------|-------------------|------------------|
| Installation | Python + dependencies | None (web browser) |
| Updates | Manual download | Automatic (deploy = update) |
| Access | Single computer | Anywhere with internet |
| CSV Editor | Built-in editor | Download & edit externally |
| Screenshots | Paste from clipboard | Upload images (can be added) |

---

## 🌐 Architecture

```
User's Browser
    ↓
Streamlit Cloud (your app)
    ↓
User's Azure DevOps (via Azure CLI)
    ↓
AI Provider (GitHub Models / OpenAI)
    ↓
Generated CSV file
```

**Important:** Each user needs:
- Access to Azure DevOps (via `az login` on their machine for CLI, or API tokens)
- Their own API key (GitHub or OpenAI)

---

## 📁 File Structure

```
testcaseGenerator/
├── app/
│   ├── streamlit_app.py          # 🆕 Web application
│   ├── testcase_generator.py     # Original desktop app
│   └── testcase_template.csv
├── .streamlit/
│   ├── config.toml                # 🆕 Streamlit configuration
│   └── secrets.toml.template      # 🆕 Secrets template
├── requirements-streamlit.txt     # 🆕 Web app dependencies
└── STREAMLIT_DEPLOYMENT.md        # 🆕 This file
```

---

## 🔐 Security Considerations

### DO NOT commit to Git:
- `.streamlit/secrets.toml` (actual secrets)
- API keys or tokens
- Azure DevOps credentials

### ADD to .gitignore:
```
.streamlit/secrets.toml
*.env
.testgen_config.json
```

### In Streamlit Cloud:
- Store all secrets in App Settings → Secrets
- Users provide their own API keys via the UI

---

## 🐛 Troubleshooting

### "Azure CLI not found"
**Solution:** The web app requires Azure CLI to be installed on the **hosting machine**. 

**Options:**
1. **For Streamlit Cloud:** Use Azure DevOps REST API instead of CLI (requires code modification)
2. **For self-hosted:** Install Azure CLI on the server
3. **Recommended:** Modify app to use Azure DevOps Python SDK

### "Model not available"
**Solution:** Check your API key has access to the selected model

### "File not saving"
**Solution:** Streamlit Cloud has ephemeral storage. Files are kept during the session but cleared on restart. Download immediately after generation.

---

## 🚀 Advanced: Deploy to Azure App Service

For more control, deploy to Azure:

1. **Create Azure App Service** (Python 3.11)
2. **Deploy code:**
   ```bash
   az webapp up --name testcase-generator --resource-group your-rg
   ```
3. **Set environment variables** in Azure Portal
4. **Install Azure CLI** in the container (update Dockerfile)

---

## 📊 Cost Comparison

| Deployment Option | Cost | Pros | Cons |
|-------------------|------|------|------|
| **Streamlit Cloud** | FREE | Easy setup, automatic updates | Limited resources, public repo required (or paid) |
| **Azure App Service** | ~$15/month | Full control, private repos | More complex setup |
| **Desktop .exe** | FREE | No server needed | Manual distribution & updates |

---

## 🎯 Next Steps

1. **Test locally:** Run `streamlit run app/streamlit_app.py`
2. **Push to GitHub:** Create repository and push code
3. **Deploy:** Go to share.streamlit.io and deploy
4. **Share:** Send the URL to your team!

---

## 🤝 Contributing

To improve the web app:
1. Edit `app/streamlit_app.py`
2. Test locally: `streamlit run app/streamlit_app.py`
3. Commit and push to GitHub
4. Streamlit Cloud auto-deploys changes!

---

**Questions?** Check [Streamlit Docs](https://docs.streamlit.io) or [Azure DevOps API Docs](https://learn.microsoft.com/en-us/rest/api/azure/devops/)
