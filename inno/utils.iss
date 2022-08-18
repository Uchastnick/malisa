[Code]

#ifndef INCLUDE_UTILS
#define INCLUDE_UTILS

const
  SHCONTCH_NOPROGRESSBOX = 4;
  SHCONTCH_RESPONDYESTOALL = 16;

procedure UnZip(ZipPath, TargetPath: string); 
var
  Shell: Variant;
  ZipFile: Variant;
  TargetFolder: Variant;
begin
  Shell := CreateOleObject('Shell.Application');

  ZipFile := Shell.NameSpace(ZipPath);
  if VarIsClear(ZipFile) then
    RaiseException(
      Format('ZIP file "%s" does not exist or cannot be opened', [ZipPath]));

  TargetFolder := Shell.NameSpace(TargetPath);
  if VarIsClear(TargetFolder) then
    RaiseException(Format('Target path "%s" does not exist', [TargetPath]));

  TargetFolder.CopyHere(
    ZipFile.Items, SHCONTCH_NOPROGRESSBOX or SHCONTCH_RESPONDYESTOALL);
end;

procedure ShowMessage(message: String);
begin
  MsgBox(message, mbInformation, MB_OK);
end;

procedure ShowError(message: String);
begin
  MsgBox(message, mbError, MB_OK);
end;

procedure GetMicrophonesInfo();
var
  ResultCode: Integer;
begin
  Exec('cmd.exe', 
       ExpandConstant('/c "{app}\malisa.exe --microphones >""{tmp}\microphones.txt"""'), 
       ExpandConstant('{app}'),
       SW_HIDE, ewWaitUntilTerminated, ResultCode);

  Exec(ExpandConstant('{tmp}\sed.exe'), 
       ExpandConstant('-i -r -n -e "s/Microphone с именем //; s/\]''//; s/ найден для ''Microphone \[device_index = /, /; s/(.+), (.+)/\2 - \1/p;" "{tmp}\microphones.txt"'),
       '',
       SW_HIDE, ewWaitUntilTerminated, ResultCode);

  Exec('cmd.exe',
       ExpandConstant('/c "{tmp}\iconv.exe -f UTF-8 -t CP1251 ""{tmp}\microphones.txt"" >""{tmp}\microphones.txt.1251"""'),
       '',
       SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure GetVoicesInfo();
var
  ResultCode: Integer;
begin
  Exec('cmd.exe', 
       ExpandConstant('/c "{app}\malisa.exe --voices >""{tmp}\voices.txt"""'),
       ExpandConstant('{app}'),
       SW_HIDE, ewWaitUntilTerminated, ResultCode);

  Exec(ExpandConstant('{tmp}\sed.exe'),
       ExpandConstant('sed -i -r -n -e "s/([^'']+)''([^'']+)''(.+)/\2/p;" "{tmp}\voices.txt"'),
       '',
       SW_HIDE, ewWaitUntilTerminated, ResultCode);

  Exec('cmd.exe',
       ExpandConstant('/c "{tmp}\iconv.exe -f UTF-8 -t CP1251 ""{tmp}\voices.txt"" >""{tmp}\voices.txt.1251"""'),
       '',
       SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure ConfigTo1251();
var
  ResultCode: Integer;
begin
  Exec('cmd.exe',
       ExpandConstant('/c "{tmp}\iconv.exe -f UTF-8 -t CP1251 ""{app}\config\config.ini"" >""{tmp}\config.ini.1251"""'),
       '',
       SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure ConfigToUTF8();
var
  ResultCode: Integer;
begin
  Exec('cmd.exe',
       ExpandConstant('/c "{tmp}\iconv.exe -f CP1251 -t UTF-8 ""{tmp}\config.ini.1251"" >""{app}\config\config.ini"""'),
       '',
       SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure AutoAcceptLicense();
var
  Page: TWizardPage;
  Component: TComponent;
  I: Integer;
begin
  Page := PageFromID(wpLicense);
  for I:=0 to TWinControl(Page.Surface).ControlCount - 1 do
    begin
      Component := TComponent(TWinControl(Page.Surface).Controls[I])
      //ShowMessage(Component.Name);
      if Component.Name = 'FLicenseAcceptedRadio' then
      begin
        TRadioButton(Component).Checked := True;
        break;
      end;
    end;
end;

#endif