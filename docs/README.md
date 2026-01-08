# Test Case Generator for Azure DevOps

A user-friendly desktop application that helps manual QA testers generate automated test cases from Azure DevOps work items.

## 🎯 Purpose

This tool simplifies the process of creating manual test cases by:
- Automatically exporting work items from Azure DevOps
- Preparing data for test case generation
- Providing a simple GUI interface for QA testers
- Eliminating the need to run command-line tools manually

## ✨ Features

- **Simple GUI Interface** - No command-line knowledge required
- **Standalone Executable** - No Python installation needed (see Distribution section)
- **One-Click Export** - Automatically exports work items from Azure DevOps
- **AI-Powered Test Case Generation** - Automatically generates comprehensive test cases using OpenAI
- **Prerequisites Check** - Verifies Azure CLI is installed
- **Activity Log** - Shows real-time progress and status
- **Error Handling** - Clear error messages and helpful guidance

## 📦 Two Ways to Use

### Option 1: Standalone Executable (Recommended for QA)

**No Python Required!** Just download and run.

1. **Get the executable**: `TestCaseGenerator.exe`
2. **Install Azure CLI**: [Download here](https://aka.ms/installazurecliwindows)
3. **Log in**: Run `az login` in PowerShell
4. **Run**: Double-click TestCaseGenerator.exe

That's it! See the [Distribution](#-distribution) section below.

### Option 2: Run from Source (For Developers)

If you want to modify the code or build your own executable, see the [Installation](#-installation) section.

## �� Building the Executable

**For Developers:** To create the standalone .exe file:

1. **Install Python** (if not already installed)

2. **Run the build script**:
   ```powershell
   build_executable.bat
   ```

3. **Find the executable**:
   - Location: `dist\TestCaseGenerator.exe`
   - Size: ~15-30 MB

4. **Distribute to QA team**:
   - Copy `TestCaseGenerator.exe` to a shared location
   - Users don't need Python installed!

For detailed build instructions, see [BUILDING.md](BUILDING.md).

---

## 📋 Prerequisites (For Running from Source)

### For QA Team Members (End Users)

**You only need:**
1. `TestCaseGenerator.exe` - The standalone application
2. Azure CLI - [Download](https://aka.ms/installazurecliwindows)
3. Run `az login` to authenticate

**Quick Start:**
1. Double-click `TestCaseGenerator.exe`
2. Click "Check Prerequisites" to verify Azure CLI
3. Enter a work item ID
4. Click "Generate Test Cases"

**Download Location:**
Contact your development team for the TestCaseGenerator.exe file, or check your team's shared drive.

---

## �📋 Prerequisites

Before using this tool, you need:

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Azure CLI**
   - Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
   - After installation, log in with: `az login`

3. **Azure DevOps Access**
   - You must have access to the Azure DevOps organization
   - You must be logged in via Azure CLI

## 🚀 Installation

### Automatic Installation (Recommended)

1. **Double-click `install_prerequisites.bat`**
   - Automatically installs Python and Azure CLI
   - Uses Windows Package Manager (winget)
   - Falls back to browser downloads if needed

2. **After installation, log in to Azure DevOps**:
   ```powershell
   az login
   ```

### Manual Installation

1. **Clone or download this repository** to your computer

2. **Install Python** from https://www.python.org/downloads/
   - Check "Add Python to PATH" during installation

3. **Install Azure CLI** from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

4. **Install Python dependencies** (if any):
   ```powershell
   pip install -r requirements.txt
   ```

5. **Verify installations**:
   ```powershell
   python --version
   az --version
   ```

6. **Log in to Azure DevOps**:
   ```powershell
   az login
   ```

## 📖 How to Use

### Step 1: Launch the Application

**Option A: Using the Launcher (Easiest)**
- Double-click `start_generator.bat`
- If Python is not installed, it will offer to install it automatically

**Option B: Direct Launch**
- Double-click `testcase_generator.py`, or run:
  ```powershell
  python testcase_generator.py
  ```

### Step 2: Check Prerequisites

1. Click the **"Check Prerequisites"** button
2. Verify that Azure CLI is installed
3. If not installed, follow the installation link provided

### Step 3: Enter Work Item Information

1. **Work Item ID**: Enter the Azure DevOps work item number (e.g., `5152532`)
2. **Organization URL**: Default is set (change if needed)
3. **Workspace Folder**: Select where to save files (default is current folder)
4. **AI Test Case Generation**: 
   - Check the box to enable automatic test case generation
   - Enter your OpenAI API key (get one from https://platform.openai.com/api-keys)
   - Or leave unchecked for manual generation

### Step 4: Generate Test Cases

1. Click **"Generate Test Cases"**
2. Watch the Activity Log for progress
3. The tool will:
   - Export the work item JSON from Azure DevOps
If you don't have an OpenAI API key, you can:

**Option A: Use GitHub Copilot**cases using AI (if enabled)
   - Save both files: `PBI-<ID>.json` and `Testcases_PBI_<ID>.csv`

### Step 5: Review and Import

1. Open `Testcases_PBI_<ID>.csv` to review the generated test cases
2. Make any necessary adjustments
3. Import the CSV into Azure DevOps Test Plans

---

## 🤖 AI Test Case Generation

The application can automatically generate comprehensive manual test cases using OpenAI's GPT-4 model.

### Setup

1. Get an OpenAI API key from: https://platform.openai.com/api-keys
2. Enter the API key in the application (it's hidden with asterisks)
3. Check "Automatically generate test cases using AI"
4. Click "Generate Test Cases"

### What It Generates

The AI creates test cases covering:
- **Functional tests (FUNC-XX)** - Core functionality testing
- **Validation tests (VAL-XX)** - Input validation and data integrity
- **UI tests (UI-XX)** - User interface and usability
- **Negative tests (NEG-XX)** - Error handling and edge cases
- **Regression tests (REG-XX)** - Ensuring existing functionality still works

### Without AI

If you don't have an OpenAI API key, you can:
1. Open the generated JSON file in VS Code
2. Open the `testcase_template.csv` file as reference
3. Ask GitHub Copilot:
   ```
   Generate manual test cases CSV from this work item JSON using the 
   testcase_template.csv format. Follow these rules:
   - No commas in text fields
   - Test Case rows and Test Step rows on separate lines
   - Include FUNC, VAL, UI, NEG, and REG test cases
   - Don't include Project, ID, Area Path, or State columns
**Option B: Manual Creation**

#### Option B: Manual Creation
1. Open the generated JSON file
2. Review the work item details, acceptance criteria, and developer notes
3. Create test cases following the template format

## 📁 Output Files

The tool generates the following files in your workspace:

- `PBI-<ID>.json` - Exported work item data from Azure DevOps
- `Testcases_PBI_<ID>.csv` - Generated test cases (created by AI/manually)

## 🎨 User Interface Guide

### Main Window Components

1. **Work Item Information Panel**
   - Enter the work item ID and other details
   - Browse to select your workspace folder

2. **Action Buttons**
   - **Generate Test Cases**: Starts the generation process
   - **Check Prerequisites**: Verifies Azure CLI installation
   - **Clear Log**: Clears the activity log

3. **Activity Log**
   - Shows real-time progress
   - Displays success/error messages
   - Provides helpful tips and next steps

4. **Status Bar**
   - Shows current operation status at the bottom

## ⚙️ Configuration

### Changing the Organization URL

If you work with a different Azure DevOps organization:
1. Change the URL in the "Organization URL" field
2. Format: `https://dev.azure.com/YOUR_ORG_NAME`

### Changing the Workspace Folder

1. Click the **"Browse..."** button
2. Select the folder where you want to save files
3. The tool will use this folder for all operations

## 🐛 Troubleshooting

### "Azure CLI is NOT installed"
- Download and install Azure CLI from the link provided
- Restart the application after installation

### "Failed to export work item"
- Verify you're logged in: `az login`
- Check you have access to the work item
- Verify the organization URL is correct

### "Work Item ID must be a number"
- Enter only the numeric ID (e.g., `5152532`)
- Don't include prefixes like "PBI-" or "BUG-"

### Command times out
- Check your internet connection
- Verify Azure DevOps service is accessible
- Try again after a few moments

## 💡 Tips for QA Testers

1. **Keep the template file handy**: Always have `testcase_template.csv` in your workspace
2. **Review the JSON**: Check the exported JSON to understand the work item before generating tests
3. **Use GitHub Copilot**: It significantly speeds up test case creation
4. **Be specific**: Pay attention to Developer Notes in the work item - they guide test coverage
5. **Batch processing**: You can generate multiple work items by running the tool multiple times

## 📚 Test Case Guidelines

When creating test cases, ensure you:

- ✅ Cover Functional (FUNC), Validation (VAL), UI, Negative (NEG), and Regression (REG) scenarios
- ✅ Include clear preconditions, steps, and expected results
- ✅ Keep steps concise and actionable
- ✅ Map tests to requirements and acceptance criteria
- ✅ Avoid commas in any text fields (CSV format requirement)
- ✅ Keep Test Case rows and Test Step rows separate

## 🔄 Workflow Example

```
1. QA receives work item: PBI-5152532
2. Open Test Case Generator app
3. Enter work item ID: 5152532
4. Click "Generate Test Cases"
5. Review exported JSON file
6. Use GitHub Copilot to create CSV
7. Review and import CSV into Azure DevOps
```

## 🤝 Support

If you encounter issues:
1. Check the Activity Log for error details
2. Verify all prerequisites are installed
3. Review the troubleshooting section
4. Contact your team lead or admin

## 📝 Version History

- **v1.0** - Initial release with GUI interface and Azure CLI integration

---

**Made with ❤️ for Manual QA Teams**
