#include <idp.iss>
; #include <idplang\russian.iss> 
; #include "environment.iss"

#include "utils.iss"
#include "optionsPage.iss"

#define MyAppName "Малиса - голосовой помощник"
#define MyAppPublisher "dsm"
#define MyAppExeName "malisa.exe"
#define DefaultDirName "c:\malisa"

#ifndef MyAppVersion
  #define MyAppVersion "2.3.2-beta"
#endif

#ifndef PythonVersion
  #define PythonVersion "cp37"
#endif

#ifndef WinVersion
  #define WinVersion "win-amd64"
#endif

#define MalisaServerLink StringChange("https://github.com/Uchastnick/malisa/releases/download/v%MyAppVersion%", "%MyAppVersion%", MyAppVersion)
#define MalisaArchive StringChange(StringChange(StringChange("malisa-%MyAppVersion%-%PythonVersion%-%WinVersion%.zip", "%MyAppVersion%", MyAppVersion), "%PythonVersion%", PythonVersion), "%WinVersion%", WinVersion)

#define RHVoiceServerLink "https://rhvoice.eu-central-1.linodeobjects.com"
#define VoiceFileArina "RHVoice-voice-Russian-Arina-v4.0.2009.14-setup"
#define VoiceFileIrina "RHVoice-voice-Russian-Irina-v4.1.2010.15-setup"

#define MPVLink "https://downloads.sourceforge.net/project/mpv-player-windows/64bit/mpv-x86_64-20220807-git-9add44b.7z"
#define AIMP3Link "https://www.aimp.ru/?do=download.file&id=4"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{7108A4A6-5564-4FB5-AF7F-D7219669A9DB}
AppName=""{#MyAppName}""
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={sd}\malisa
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
InfoBeforeFile=README.ru.md
InfoAfterFile=POSTINSTAL_INFO.ru.md
OutputDir=_release
OutputBaseFilename=malisa-{#MyAppVersion}-{#PythonVersion}-win-setup
Compression=lzma
SolidCompression=yes
DisableStartupPrompt=False
DisableWelcomePage=False
AlwaysShowDirOnReadyPage=True
AllowRootDirectory=True
DisableDirPage=no
PrivilegesRequired=none
AppCopyright=dsm
; WizardSizePercent=120
; MinVersion=0,6.0

[CustomMessages]
OptionsPageName=Установка параметров
OptionsPageDescription=Основные опции программы

[LangOptions]
DialogFontSize=10
WelcomeFontSize=12
TitleFontSize=32
CopyrightFontSize=10

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"; LicenseFile: "LICENSE.en"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"; LicenseFile: "LICENSE.ru"

[Types]
Name: "full"; Description: "Полная установка"
Name: "compact"; Description: "Минимальная установка"
Name: "custom"; Description: "Выборочная установка"; Flags: iscustom

[Components]
Name: "main"; Description: "Ядро голосового помощника"; Types: full compact custom; Flags: fixed
Name: "arinavoice"; Description: "Голос 'Арина' от RHVoice"; Types: full compact custom; Flags: fixed
//Name: "main"; Description: "Ядро голосового помощника"; Types: full compact custom;
//Name: "arinavoice"; Description: "Голос 'Арина' от RHVoice"; Types: full compact custom;
Name: "irinavoice"; Description: "Голос 'Ирина' от RHVoice"; Types: full
Name: "mpvplayer"; Description: "Локальная установка плеера MPV"; Types: full
Name: "aimp3player"; Description: "Установка плеера AIMP3"; Types: full

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Source: "unzip.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall
Source: "7za.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall
Source: "sed.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall
Source: "iconv.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall
Source: "{tmp}\malisa\malisa.exe"; DestDir: "{app}"; Flags: external ignoreversion
Source: "{tmp}\malisa\*"; DestDir: "{app}"; Flags: external ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Малиса - отложенный запуск"; Filename: "{app}\script\malisa.bat"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Малиса - список микрофонов"; Filename: "{app}\script\1_malisa_microphones.bat"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Малиса - список доступных голосов"; Filename: "{app}\script\2_malisa_voices.bat"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Малиса - редактирование параметров"; Filename: "notepad.exe"; Parameters: "{app}\config\config.ini"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{commondesktop}\Малиса - отложенный запуск"; Filename: "{app}\script\malisa.bat"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{commondesktop}\Малиса - список микрофонов"; Filename: "{app}\script\1_malisa_microphones.bat"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{commondesktop}\Малиса - список доступных голосов"; Filename: "{app}\script\2_malisa_voices.bat"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{commondesktop}\Малиса - редактирование параметров"; Filename: "notepad.exe"; Parameters: "{app}\config\config.ini"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{tmp}\{#VoiceFileArina}.exe"; Flags: skipifsilent runascurrentuser; Description: "Установка голоса 'Арина'"; Components: arinavoice
Filename: "{tmp}\{#VoiceFileIrina}.exe"; Flags: skipifsilent runascurrentuser; Description: "Установка голоса 'Ирина'"; Components: irinavoice
Filename: "{tmp}\7za.exe"; Parameters: "x -y -o{app}\tools\mpv {tmp}\mpv.7z"; Flags: runhidden; Description: "Локальная установка плеера MPV в каталог 'malisa/tools/mpv'"; Components: mpvplayer
Filename: "{tmp}\aimp_setup.exe"; Description: "Установка плеера AIMP3"; Components: aimp3player
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[INI]
//Filename: "{app}\config\config.ini"; Section: "app"; Key: "MPV_APP_PATH"; String: "'{app}\\tools\\mpv\\mpv'"; Components: mpvplayer
Filename: "{app}\config\config.ini"; Section: "app"; Key: "SET_VOLUME_APP"; String: "'{app}\\tools\\setvol\\setvol.exe'"; Components: main

[Code]

var
  options1PageId, options2PageId: Integer;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then 
  begin    
    if WizardIsComponentSelected('main') then
    begin
      UnZip(ExpandConstant('{tmp}\{#MalisaArchive}'), ExpandConstant('{tmp}'));
      if WizardIsComponentSelected('arinavoice') then UnZip(ExpandConstant('{tmp}\malisa\_distr\{#VoiceFileArina}.zip'), ExpandConstant('{tmp}'));
    end;
  end;

  if CurStep = ssPostInstall then
  begin
    FileCopy(ExpandConstant('{app}\config\config.in_'), ExpandConstant('{app}\config\config.ini'), true);
    FileCopy(ExpandConstant('{app}\config\smart_devices.yam_'), ExpandConstant('{app}\config\smart_devices.yaml'), true);
    
    GetMicrophonesInfo();
    GetVoicesInfo();

    ConfigTo1251();

    options1PageId := CreateOptions1Page(wpInfoAfter);
    options2PageId := CreateOptions2Page(options1PageId, WizardIsComponentSelected('mpvplayer'));

    //EnvAddPath(ExpandConstant('{app}'));
  end;

  if CurStep = ssDone then 
  begin
    ConfigToUTF8();
  end;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  //if CurPageID = wpLicense then AutoAcceptLicense();

  //if (CurPageID = options1PageId) or (CurPageID = options2PageId) then
  //begin
  //end;

  //if CurPageID = wpFinished then
  //begin
  //end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then 
  begin
    //EnvRemovePath(ExpandConstant('{app}'));
  end;
end;

procedure InitializeWizard();
begin    
  idpAddFileComp(ExpandConstant('{#MalisaServerLink}/{#MalisaArchive}'), ExpandConstant('{tmp}\{#MalisaArchive}'), 'main');
  idpAddFileComp(ExpandConstant('{#RHVoiceServerLink}/{#VoiceFileIrina}.exe'), ExpandConstant('{tmp}\{#VoiceFileIrina}.exe'), 'irinavoice');
  idpAddFileComp(ExpandConstant('{#MPVLink}'), ExpandConstant('{tmp}\mpv.7z'), 'mpvplayer');
  idpAddFileComp(ExpandConstant('{#AIMP3Link}'), ExpandConstant('{tmp}\aimp_setup.exe'), 'aimp3player');

  idpDownloadAfter(wpReady);
end;
