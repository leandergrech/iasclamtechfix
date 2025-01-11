[Setup]
AppName=iASClamTechFix
AppVersion=1.0
DefaultDirName={pf}\iasclamtechfix
DefaultGroupName=iASClamTechFix
OutputBaseFilename=iASClamTechFixInstaller
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\gui.exe
Uninstallable=yes

[Files]
Source: "dist\gui.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\iASClamTechFix"; Filename: "{app}\gui.exe"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"
Name: "{commondesktop}\iASClamTechFix"; Filename: "{app}\gui.exe"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"
Name: "{group}\Uninstall iASClamTechFix"; Filename: "{uninstallexe}"


[Run]
Filename: "{app}\gui.exe"; Description: "Launch iASClamTechFix"; Flags: nowait postinstall skipifsilent
