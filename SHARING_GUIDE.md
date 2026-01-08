# Test Case Generator - Sharing Guide

## 🎯 You've Built the Standalone Executable!

**Location:** `dist\TestCaseGenerator.exe` (71.37 MB)

---

## 📤 How to Share with Your Team

### Option 1: Direct File Share (Easiest)

1. **Copy the .exe:**
   ```
   dist\TestCaseGenerator.exe
   ```

2. **Share via:**
   - Email (if your email allows 71 MB attachments)
   - Microsoft Teams
   - SharePoint
   - Network drive

3. **Tell your team:**
   - Double-click to run (no Python installation needed!)
   - Azure CLI must still be installed: https://aka.ms/installazurecliwindows
   - They'll need to run `az login` the first time

### Option 2: Create a Zip Package

```powershell
# Create a zip with the executable and documentation
Compress-Archive -Path dist\TestCaseGenerator.exe, README.md, docs\* -DestinationPath TestCaseGenerator-Portable.zip
```

Then share `TestCaseGenerator-Portable.zip`

---

## ✨ What Your Team Gets

### ✅ Included in the .exe:
- Python interpreter
- All Python libraries (tkinter, pandas, PIL, etc.)
- Full application logic
- Works on any Windows 10/11 PC (no installation!)

### ⚠️ Still Required:
- **Azure CLI** - For exporting work items from Azure DevOps
  - Download: https://aka.ms/installazurecliwindows
  - Run once: `az login`
  
- **AI API Keys** - Users provide their own:
  - GitHub Models (free): https://github.com/marketplace/models
  - OpenAI (paid): https://platform.openai.com
  - Anthropic (paid): https://console.anthropic.com

---

## 🖥️ Desktop App vs Streamlit App

You built the **tkinter desktop app** (traditional Windows GUI).

### Desktop App Features:
✅ Single .exe file (easy to share)
✅ Familiar Windows interface
✅ Works offline (after initial AzDO export)
✅ Built-in CSV editor
✅ Clipboard screenshot support

### If You Want the Web App Instead:
The **Streamlit version** offers:
- Modern web interface
- Access from any browser
- Easier remote access
- Preview with auto-save

To build a Streamlit portable app, you'd need a different approach (local server + batch file).

---

## 🚀 Quick Test

Run it yourself first:
```powershell
.\dist\TestCaseGenerator.exe
```

Expected:
1. Window opens with Azure DevOps login
2. Enter work item ID
3. Generate test cases
4. Export CSV

---

## 📋 Team Instructions Template

Copy this for your team:

```
Hi Team,

I've created a tool to automate test case generation from Azure DevOps work items!

SETUP (one-time):
1. Install Azure CLI: https://aka.ms/installazurecliwindows
2. Run in PowerShell: az login
3. Get a GitHub Models API key (free): https://github.com/marketplace/models

USAGE:
1. Double-click TestCaseGenerator.exe
2. Enter your API key
3. Enter a PBI/Bug number from Azure DevOps
4. Click Generate Test Cases
5. Review, edit, and export the CSV

The tool generates functional, validation, UI, negative, and regression test cases automatically!

Questions? Let me know!
```

---

## 🔧 Troubleshooting

### "Windows protected your PC" warning
- Click "More info" → "Run anyway"
- This is normal for unsigned executables
- To avoid: Code-sign the .exe (requires certificate ~$200/year)

### "Azure CLI not found"
- User needs to install Azure CLI
- After install, restart the .exe

### Large file size (71 MB)
- This includes entire Python + all libraries
- Normal for PyInstaller bundles
- Compressed zip would be ~30-40 MB

---

## 🎁 Next Steps

**For wider distribution:**
1. Create a Teams/SharePoint folder for the .exe
2. Add README.md for documentation
3. Set up a feedback channel
4. Update the .exe when you make improvements

**For continuous updates:**
Consider moving to Streamlit Cloud where updates are automatic!

---

**Congratulations!** 🎉 You're ready to share your test case generator!
