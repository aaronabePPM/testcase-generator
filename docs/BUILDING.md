# Building the Standalone Executable

This guide explains how to build a standalone Windows executable (.exe) that doesn't require Python to be installed.

## Prerequisites for Building

- Python 3.8 or higher (only needed once to build)
- PyInstaller (will be installed automatically by the build script)

## Quick Build

1. **Run the build script**:
   ```powershell
   build_executable.bat
   ```

2. **Wait for completion** (typically 2-5 minutes)

3. **Find your executable**:
   - Location: `dist\TestCaseGenerator.exe`
   - Size: ~15-30 MB (includes Python runtime)

## Manual Build (Advanced)

If you prefer to build manually:

```powershell
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller --onefile --windowed --name "TestCaseGenerator" testcase_generator.py
```

Or use the spec file for more control:

```powershell
pyinstaller TestCaseGenerator.spec
```

## Distribution

Once built, you can:

1. **Copy the .exe anywhere** - it's completely standalone
2. **Share with your team** - they don't need Python installed
3. **Run directly** - just double-click TestCaseGenerator.exe

### What Users Need

✅ The executable file (TestCaseGenerator.exe)  
✅ Azure CLI installed and configured (`az login`)  
✅ Access to Azure DevOps  
❌ Python (NOT required!)

## File Structure After Building

```
BacklogItems/
├── dist/
│   └── TestCaseGenerator.exe    ← The standalone executable
├── build/                        ← Temporary build files (can delete)
└── TestCaseGenerator.spec        ← Build configuration
```

## Distribution Package

To create a distribution package for your QA team:

1. Copy `TestCaseGenerator.exe` to a new folder
2. Include `testcase_template.csv` (required for template)
3. Create a shortcut on the desktop (optional)
4. Add a README with these instructions:

```
Test Case Generator - Quick Start
==================================

1. Install Azure CLI: https://aka.ms/installazurecliwindows
2. Run: az login
3. Double-click TestCaseGenerator.exe
4. Enter work item ID and click "Generate Test Cases"

That's it! No Python required.
```

## Troubleshooting

### Build fails with "Unable to find module"
- Make sure all imports in testcase_generator.py are standard library
- Currently the app uses only tkinter (built-in), so this shouldn't happen

### Executable is very large
- Normal! It includes the entire Python runtime
- Typical size: 15-30 MB
- You can enable UPX compression to reduce size (already enabled in spec file)

### Antivirus flags the executable
- Common with PyInstaller executables
- Add an exception for TestCaseGenerator.exe
- Or sign the executable with a code signing certificate

### Executable won't run on other computers
- Ensure they have Windows 10 or later
- Try building with --onefile flag (already default)
- Check Windows Defender isn't blocking it

## Advanced Options

### Add an icon

1. Create or download an .ico file
2. Update the build command:
   ```powershell
   pyinstaller --onefile --windowed --icon=app_icon.ico --name "TestCaseGenerator" testcase_generator.py
   ```

### Include additional files

If you need to bundle files like the CSV template:

```powershell
pyinstaller --onefile --windowed --add-data "testcase_template.csv;." --name "TestCaseGenerator" testcase_generator.py
```

### Debug mode

To see console output for debugging:

```powershell
pyinstaller --onefile --console --name "TestCaseGenerator" testcase_generator.py
```

## Updating the Executable

When you update testcase_generator.py:

1. Delete the `build` and `dist` folders
2. Run `build_executable.bat` again
3. Distribute the new TestCaseGenerator.exe

## Performance Notes

- First launch may be slower (extracts to temp folder)
- Subsequent launches are faster
- Consider using `--onedir` instead of `--onefile` for faster startup
  (creates a folder with multiple files instead of single .exe)
