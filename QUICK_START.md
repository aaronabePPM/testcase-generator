# 🚀 Quick Reference Card

## Test the Web App NOW

```bash
# Option 1: Direct command
streamlit run app/streamlit_app.py

# Option 2: Use launcher
launchers\start_streamlit.bat
```

**Browser will open at:** `http://localhost:8501`

---

## Deploy to Streamlit Cloud

### 3 Steps to Live Web App:

**1. Push to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit with Streamlit app"
git remote add origin https://github.com/YOUR-USERNAME/testcase-generator.git
git push -u origin main
```

**2. Go to:** https://share.streamlit.io

**3. Deploy:**
- Click "New app"
- Select your repo: `YOUR-USERNAME/testcase-generator`
- Main file: `app/streamlit_app.py`
- Click "Deploy"

**Done! Share the URL with your team! 🎉**

---

## File Changes Summary

### ✨ New Files Created:
```
✅ app/streamlit_app.py              (396 lines - Web application)
✅ requirements-streamlit.txt         (Streamlit dependencies)
✅ .streamlit/config.toml            (App configuration)
✅ .streamlit/secrets.toml.template  (Secrets template)
✅ launchers/start_streamlit.bat     (Windows launcher)
✅ launchers/start_streamlit.ps1     (PowerShell launcher)
✅ .gitignore                        (Git rules)
✅ docs/STREAMLIT_DEPLOYMENT.md      (Full guide)
✅ STREAMLIT_CONVERSION.md           (This guide)
```

### 📝 Updated Files:
```
✅ README.md                         (Added web version info)
```

### 💯 Preserved:
```
✅ app/testcase_generator.py         (Original desktop app - still works!)
✅ All launchers & utilities         (Desktop version intact)
✅ Data folder structure             (No changes)
```

---

## Quick Commands

### Local Development:
```bash
# Desktop app
python app/testcase_generator.py

# Web app
streamlit run app/streamlit_app.py
```

### Install Dependencies:
```bash
# Desktop
pip install -r requirements.txt

# Web
pip install -r requirements-streamlit.txt
```

### Build Desktop .exe:
```bash
launchers\build_executable.bat
```

---

## URLs to Bookmark

- **Deploy:** https://share.streamlit.io
- **Docs:** https://docs.streamlit.io
- **Community:** https://discuss.streamlit.io
- **Azure CLI:** https://aka.ms/installazurecliwindows

---

## Comparison at a Glance

| Feature | Desktop | Web |
|---------|---------|-----|
| Launch | `.bat` file | URL link |
| Installation | Python + deps | None |
| Access | Local only | Anywhere |
| Updates | Re-download | Automatic |
| Offline | ✅ | ❌ |
| CSV Editing | Full editor | Download |
| Screenshots | Paste | Upload* |
| Team Sharing | Send .exe | Share URL |

**Both versions work side-by-side!**

---

## Troubleshooting

### "streamlit not found"
```bash
pip install streamlit
```

### "Azure CLI not found"
```bash
# Install from: https://aka.ms/installazurecliwindows
az login
```

### Port already in use
```bash
streamlit run app/streamlit_app.py --server.port 8502
```

### Fresh start
```bash
streamlit cache clear
```

---

## Security Checklist

Before deploying:
- ✅ Check `.gitignore` includes `secrets.toml`
- ✅ Don't commit API keys
- ✅ Use Streamlit Cloud secrets for tokens
- ✅ Each user provides their own API keys

---

## Next Actions

**Today:**
1. ✅ Test locally
2. ✅ Verify work item export
3. ✅ Test AI generation

**This Week:**
1. ✅ Push to GitHub
2. ✅ Deploy to Streamlit Cloud
3. ✅ Share with team

**Next Month:**
- Add screenshot upload
- Implement inline editing
- Add analytics dashboard

---

## 🎉 You're Ready!

**Desktop app:** `launchers\start_generator.bat`
**Web app:** `launchers\start_streamlit.bat`
**Deploy:** Push to GitHub → share.streamlit.io

**Questions?** See `STREAMLIT_CONVERSION.md` or `docs/STREAMLIT_DEPLOYMENT.md`
