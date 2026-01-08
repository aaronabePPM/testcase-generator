# Test Case Generator for Azure DevOps

A user-friendly application that helps manual QA testers generate automated test cases from Azure DevOps work items.

## 🎯 Two Versions Available

### 🖥️ Desktop App (Original)
Traditional Windows application with full offline capabilities
- **Best for:** Individual users, offline work, direct file editing
- **Launch:** `launchers/start_generator.bat`

### 🌐 Web App (NEW!)
Modern web application accessible from any browser
- **Best for:** Teams, remote access, easy deployment
- **Launch:** `launchers/start_streamlit.bat`
- **Deploy:** [See Deployment Guide](docs/STREAMLIT_DEPLOYMENT.md)

---

## 🚀 Quick Start

### Desktop Version

1. **Install Azure CLI**: [Download here](https://aka.ms/installazurecliwindows)
2. **Log in to Azure**: Run `az login` in PowerShell
3. **Run the application**: Double-click `launchers/start_generator.bat`

### Web Version

1. **Install dependencies:**
   ```bash
   pip install -r requirements-streamlit.txt
   ```

2. **Run the app:**
   ```bash
   streamlit run app/streamlit_app.py
   ```
   Or double-click: `launchers/start_streamlit.bat`

3. **Open browser:** Navigate to `http://localhost:8501`

---

## 📁 Project Structure

```
testcaseGenerator/
├── app/                          # Application source files
│   ├── testcase_generator.py    # Desktop application (tkinter)
│   ├── streamlit_app.py         # 🆕 Web application (Streamlit)
│   └── testcase_template.csv    # Template for test cases
│
├── launchers/                    # Launch scripts
│   ├── start_generator.bat      # Desktop app launcher
│   ├── start_streamlit.bat      # 🆕 Web app launcher  
│   ├── start_streamlit.ps1      # 🆕 Web app launcher (PowerShell)
│   ├── Launch-TestCaseGenerator.ps1  # Desktop launcher (PS)
│   ├── build_executable.bat     # Build standalone .exe
│   ├── install_prerequisites.bat # Install Python & Azure CLI
│   └── check_python.bat         # Diagnose Python installation
│
├── data/                         # Generated files (auto-created)
│   ├── json/                    # PBI JSON exports from Azure DevOps
│   └── testcases/               # Generated test case CSV files
│
├── .streamlit/                   # 🆕 Streamlit configuration
│   ├── config.toml              # App settings
│   └── secrets.toml.template    # Secrets template
│
├── docs/                         # Documentation
│   ├── README.md                # Full documentation
│   ├── BUILDING.md              # Build instructions
│   ├── STREAMLIT_DEPLOYMENT.md  # 🆕 Web deployment guide
│   └── ManualTestCasesGeneration-prompt.txt
│
├── requirements.txt              # Desktop app dependencies
├── requirements-streamlit.txt    # 🆕 Web app dependencies
├── TestCaseGenerator.spec        # PyInstaller spec file
├── .gitignore                    # 🆕 Git ignore rules
└── mcp.json                      # MCP configuration
```

## 📖 Documentation

For complete documentation, see [docs/README.md](docs/README.md)

## 🔧 Development

### Building the Executable

```powershell
.\launchers\build_executable.bat
```

The standalone .exe will be created in the `dist/` folder.

### Installing Dependencies

### Both Versions
- ✅ **AI-Powered Test Case Generation** - Uses OpenAI or GitHub Models
- ✅ **Automatic Azure DevOps Export** - One-click work item export
- ✅ **CSV Editor** - Edit test cases directly
- ✅ **Organized Output** - All JSON and CSV files saved to `data/` folder

### Desktop Only
- ✅ **Screenshot Analysis** - Enhance test cases with UI screenshots
- ✅ **Built-in CSV Editor** - Full spreadsheet-like editing
- ✅ **Offline Capable** - Works without internet (after setup)
- ✅ **Standalone .exe** - No Python required for end users

### Web Only  
- ✅ **Browser-Based** - Access from anywhere
- ✅ **Real-Time Preview** - See results as they generate
- ✅ **Instant Updates** - Deploy once, everyone gets updates
- ✅ **Mobile-Friendly** - Responsive design
- ✅ **FREE Hosting** - Deploy to Streamlit Cloud for free

---

## 📖 Documentation

- **Desktop App:** [docs/README.md](docs/README.md)
- **Web Deployment:** [docs/STREAMLIT_DEPLOYMENT.md](docs/STREAMLIT_DEPLOYMENT.md)
- **Building .exe:** [docs/BUILDING.md](docs/BUILDING.md)

---

## 🔧 Development

### Run Desktop App (Development)
```bash
python app/testcase_generator.py
```

### Run Web App (Development)
```bash
streamlit run app/streamlit_app.py
```

### Building the Executable
```powershell
.\launchers\build_executable.bat
```

### Installing Dependencies
```bash
# Desktop app
pip install -r requirements.txt

# Web app
pip install -r requirements-streamlit.txt
```

---

## 🌐 Deploy Web App to Cloud

### Option 1: Streamlit Cloud (FREE)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and deploy
4. See [docs/STREAMLIT_DEPLOYMENT.md](docs/STREAMLIT_DEPLOYMENT.md) for details

### Option 2: Azure App Service
1. Create App Service (Python 3.11)
2. Deploy via Azure CLI or GitHub Actions
3. Configure environment variables

---

## 📊 Version Comparison

| Feature | Desktop | Web |
|---------|---------|-----|
| **Installation** | Python + deps | None (browser) |
| **Access** | Single computer | Anywhere |
| **Updates** | Manual download | Automatic |
| **CSV Editor** | Full built-in editor | Download & edit |
| **Screenshots** | Paste from clipboard | Future feature |
| **Offline** | ✅ Yes | ❌ No |
| **Team Sharing** | Manual .exe distribution | URL link |
| **Cost** | Free | Free (Streamlit Cloud) |

---
- **Simple GUI Interface** - No command-line knowledge required
- **AI-Powered Test Case Generation** - Uses OpenAI or GitHub Models
- **Automatic Azure DevOps Export** - One-click work item export
- **CSV Editor** - Edit test cases directly in the app
- **Screenshot Analysis** - Enhance test cases with UI screenshots
- **Organized Output** - All JSON and CSV files saved to `data/` folder

## 🆘 Support

- Check [docs/README.md](docs/README.md) for detailed instructions
- Run `launchers/check_python.bat` to diagnose Python issues
- Run `launchers/install_prerequisites.bat` to install requirements

---

**Generated Files**: All PBI JSON files are saved to `data/json/` and test case CSV files to `data/testcases/`
