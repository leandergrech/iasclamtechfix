# Dependencies
`pip.exe install pypdf2 pyinstaller`

# Create wizard
 - First package the code into an EXE using pyinstaller. Navigate to `iasclamtechfix\iasclamtechfix\` and run the following:
	``` 
	python.exe -m pyinstaller.exe --onefile --noconsole --icon=icon.ico gui.py
	```
 - This should create a `dist\` directory containing the EXE .
 - Install Inno Setup Compiler on a Windows machine and open `installer.iss`.
 - Press `Compile` and a new directory called `Output` is created which contains the iASClamTechFixInstaller wizard.

# Install
 - Double click on `iASClamTechFixInstaller.exe` to install the tool.
 - Desktop and Start Menu shortcuts created by installer.
 - Uninstall shortcut also available in Start Menu.

# Usage
 - Browse for directory containing the documents with the original iAS logo.
 - Browse for the replacement logo (Note: only 287x230 px image supported for now).
 - Choose a save directory (Note: will be created if it does not exist).
