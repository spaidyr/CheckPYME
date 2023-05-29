; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "CheckPYME"
#define MyAppVersion "1.0"
#define MyAppPublisher "TFM UEM MUSTIC_2023"
#define MyAppURL "https://github.com/spaidyr/CheckPYME"
#define MyAppExeName "client.exe"
#define MyAppAssocName MyAppName + ""
#define MyAppAssocExt ".myp"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{559ED8F8-A74A-4123-9AE9-7BEE46AF38C1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
ChangesAssociations=yes
DisableProgramGroupPage=yes
LicenseFile=C:\Users\DIEGO\Dropbox\UEM\TFM\CheckPYME\LICENSE.txt
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=C:\Users\DIEGO\Dropbox\UEM\TFM\CheckPYME\Installer
OutputBaseFilename=Setup
SetupIconFile=C:\Users\DIEGO\Dropbox\UEM\TFM\CheckPYME\Agent\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startonboot"; Description: "Start {#MyAppName} on system startup"; GroupDescription: "Additional tasks"; Flags: unchecked

[Files]
Source: "C:\Users\DIEGO\Dropbox\UEM\TFM\CheckPYME\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\DIEGO\Dropbox\UEM\TFM\CheckPYME\Agent\certs\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\DIEGO\Dropbox\UEM\TFM\CheckPYME\Agent\modules\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\DIEGO\Dropbox\UEM\TFM\CheckPYME\Agent\config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\DIEGO\Dropbox\UEM\TFM\CheckPYME\Agent\agent.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\DIEGO\Dropbox\UEM\TFM\CheckPYME\Agent\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Registry]
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".myp"; ValueData: ""
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""


[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: {cmd}; Parameters: "/C sc create MyServiceName binPath= ""{app}\{#MyAppExeName}"" start= auto"; Flags: runhidden
Filename: {cmd}; Parameters: "/C sc start MyServiceName"; Flags: runhidden
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: {cmd}; Parameters: "/C sc stop MyServiceName"; Flags: runhidden
Filename: {cmd}; Parameters: "/C sc delete MyServiceName"; Flags: runhidden


