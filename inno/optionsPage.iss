#include "utils.iss"

[Code]

procedure Options1PageActivate(Page: TWizardPage);
begin
end;

function Options1PageNextButtonClick(Page: TWizardPage): Boolean;
var
  sIniFile: String;
  
  Text: String;
  Index: Integer;
  RobotName: String;
  MicIndex: Integer;
  SpeechName: String;
  SpeechRate: Integer;
begin
  Result := True;
  sIniFile := ExpandConstant('{tmp}\config.ini.1251');

  if Result then
  begin
    RobotName := Trim(TEdit(Page.FindComponent('edName')).Text);
    if RobotName = '' then begin ShowError('Не указано имя робота!'); Result := False; end;
  end;

  if Result then
  begin
    Text := Trim(TComboBox(Page.FindComponent('cbMicrophones')).Text);
    Index := TComboBox(Page.FindComponent('cbMicrophones')).ItemIndex;        
    if (Text = '') or (Index = -1) then begin ShowError('Не указан индекс микрофона!'); Result := False; end;
    if Result then
    begin
      MicIndex := Index;
      if ((MicIndex < 0) or (MicIndex > 200)) then begin ShowError('Указан недопустимый индекс микрофона!'); Result := False; end;
    end;
  end;
  
  if Result then
  begin
    SpeechName := Trim(TComboBox(Page.FindComponent('cbVoices')).Text);
    if SpeechName = '' then begin ShowError('Не указано имя голосового движка!'); Result := False; end;
  end;

  if Result then
  begin
    Text := Trim(TEdit(Page.FindComponent('edSpeechRate')).Text);
    if Text = '' then begin ShowError('Не указан параметр скорости речи!'); Result := False; end;
    if Result then
    begin
      SpeechRate := StrToInt(Text);
      if ((SpeechRate < 50) or (SpeechRate > 1000)) then begin ShowError('Указан недопустимый параметр скорости речи!'); Result := False; end;
    end;
  end;
  
  if Result then Result := SetIniString('main', 'ROBOT_NAME', '''' + RobotName + '''', sIniFile);
  if Result then Result := SetIniInt('mic', 'MICROPHONE_INDEX', MicIndex, sIniFile);
  if Result then Result := SetIniString('engine', 'SPEECH_ENGINE_RU_NAME', '''' + SpeechName + '''', sIniFile);
  if Result then Result := SetIniInt('engine', 'SPEECH_RATE_RU', SpeechRate, sIniFile);
  
  //Result := True;
end;

procedure Options1PageCancel(Page: TWizardPage; var ACancel, AConfirm: Boolean);
begin
end;

procedure Options2PageActivate(Page: TWizardPage);
begin
end;

function Options2PageNextButtonClick(Page: TWizardPage): Boolean;
var
  sIniFile: String;
  
  MPVPath: String;
  AIMPPath: String;
  BooksLibraryPath: String;
begin
  Result := True;
  sIniFile := ExpandConstant('{tmp}\config.ini.1251');

  if Result then
  begin
    MPVPath := Trim(TEdit(Page.FindComponent('edMPVPath')).Text);
    if MPVPath = '' then begin ShowError('Не указан путь к плееру MPV!'); Result := False; end;
  end;

  if Result then
  begin
    AIMPPath := Trim(TEdit(Page.FindComponent('edAIMPPath')).Text);
    if AIMPPath = '' then begin ShowError('Не указан путь к плееру AIMP!'); Result := False; end;
  end;

  if Result then
  begin
    BooksLibraryPath := Trim(TEdit(Page.FindComponent('edBooksLibraryPath')).Text);
  end;

  if Result then
  begin
    StringChangeEx(MPVPath, '\', '\\', True);
    StringChangeEx(AIMPPath, '\', '\\', True);
    StringChangeEx(BooksLibraryPath, '\', '\\', True);
  end;
  
  if Result then Result := SetIniString('app', 'MPV_APP_PATH', '''' + MPVPath + '''', sIniFile);
  if Result then Result := SetIniString('app', 'AIMP_PATH', '''' + AIMPPath + '''', sIniFile);
  if Result then Result := SetIniString('reading', 'EXTERNAL_LIBRARY_OF_BOOKS_PATH', '''' + BooksLibraryPath + '''', sIniFile);
  
  //Result := True;
end;

procedure Options2PageCancel(Page: TWizardPage; var ACancel, AConfirm: Boolean);
begin
end;

procedure GetLibraryPathOnClick(Sender: TObject);
var                        
  ExtLibraryDir: String;
  I: Integer;
  Component: TComponent;
begin  
  ExtLibraryDir := '';
  if BrowseForFolder('Выбор внешней директории для библиотеки книг', ExtLibraryDir, True) then
  begin
    for I:=0 to TWinControl(TButton(Sender).Parent).ControlCount - 1 do
      begin
        Component := TComponent(TWinControl(TButton(Sender).Parent).Controls[I]);
        if Component.Name = 'edBooksLibraryPath' then
        begin
          TEdit(Component).Text := ExtLibraryDir;
          break;
        end;
      end;
  end;
end;

procedure GetMPVPathOnClick(Sender: TObject);
var                        
  FileName: String;
  I: Integer;
  Component: TComponent;
begin  
  FileName := '';
  if GetOpenFileName('Выбор пути к плееру MPV', FileName, ExpandConstant('{app}\tools'), 
                     'MPV player (*.com)|*.com|MPV player (*.exe)|*.exe',
                     'exe') \
  then
  begin
    for I:=0 to TWinControl(TButton(Sender).Parent).ControlCount - 1 do
      begin
        Component := TComponent(TWinControl(TButton(Sender).Parent).Controls[I]);
        if Component.Name = 'edMPVPath' then
        begin
          TEdit(Component).Text := FileName;
          break;
        end;
      end;
  end;
end;

procedure GetAIMPPathOnClick(Sender: TObject);
var                        
  FileName: String;
  I: Integer;
  Component: TComponent;
begin  
  FileName := '';
  if GetOpenFileName('Выбор пути к плееру AIMP', FileName, ExpandConstant('{pf32}'), 
                     'AIMP player (*.exe)|*.exe',
                     'exe') \
  then
  begin
    for I:=0 to TWinControl(TButton(Sender).Parent).ControlCount - 1 do
      begin
        Component := TComponent(TWinControl(TButton(Sender).Parent).Controls[I]);
        if Component.Name = 'edAIMPPath' then
        begin
          TEdit(Component).Text := FileName;
          break;
        end;
      end;
  end;
end;

//=============================================================================
//== Форма установки параметров ===============================================

function CreateOptions1Page(const AfterID: Integer): Integer;
var
  Page: TWizardPage;
  
  lblName: TLabel;
  edName: TEdit;
  lblMicNumber: TLabel;
  cbMicrophones: TComboBox;
  lblSpeechName: TLabel;
  cbVoices: TComboBox;
  lblSpeechRate: TLabel;
  edSpeechRate: TEdit;

  sIniFile: String;
  
  MicIndex: Integer;
  VoiceName: String;
  VoiceIndex: Integer;
  i: Integer;
begin
  sIniFile := ExpandConstant('{tmp}\config.ini.1251');

  Page := CreateCustomPage(
    AfterID, 
    ExpandConstant('{cm:OptionsPageName}'), 
    ExpandConstant('{cm:OptionsPageDescription}'));

  { Robot's Name }
  lblName := Tlabel.Create(Page);
  with lblName do
  begin
    Parent := Page.Surface;
    Caption := 'Имя робота';
    Left := ScaleX(8);
    Top := ScaleY(3);
    Width := ScaleX(250);
    Height := ScaleY(13);
    Font.Style := [fsBold];
  end;

  edName := TEdit.Create(Page);
  with edName do
  begin
    Name := 'edName';
    Parent := Page.Surface;
    Left := lblName.Left;
    Top := lblName.Top + lblName.Height + 5;
    Width := ScaleX(401);
    Height := ScaleY(21);
    Color := TColor($FFFFFF);
    TabOrder := 0;
    Text := GetIniString('main', 'ROBOT_NAME', 'Алиса', sIniFile);
  end;

  { Microphone number (index) }
  lblMicNumber := Tlabel.Create(Page);
  with lblMicNumber do
  begin
    Parent := Page.Surface;
    Caption := 'Индекс (номер) микрофона';
    Left := lblName.Left;
    Top := edName.Top + edName.Height + 10;
    Width := ScaleX(250);
    Height := ScaleY(13);
    Font.Style := [fsBold];
    Font.Color := TColor($800080);
  end;

  cbMicrophones := TComboBox.Create(Page);
  with cbMicrophones do
  begin
    Name := 'cbMicrophones';
    Parent := Page.Surface;
    Left := lblName.Left;
    Top := lblMicNumber.Top + lblMicNumber.Height + 5;
    Width := ScaleX(401);
    Height := ScaleY(21);
    Color := TColor($FFFFFF);
    TabOrder := 1;
    Items.LoadFromFile(ExpandConstant('{tmp}\microphones.txt.1251'));
    Style := csDropDownList;    
  end;

  MicIndex := GetIniInt('mic', 'MICROPHONE_INDEX', 1, 0, 200, sIniFile);  
  
  if cbMicrophones.Items.Count = 0 then
  begin
    MicIndex := 0;
    cbMicrophones.Items.Insert(0, '0 - Default');
    cbMicrophones.ItemIndex := 0;
  end else
  begin
    if MicIndex > (cbMicrophones.Items.Count - 1) then MicIndex := -1;
    cbMicrophones.ItemIndex := MicIndex;
  end;

  { Speech engine name }
  lblSpeechName := Tlabel.Create(Page);
  with lblSpeechName do
  begin
    Parent := Page.Surface;
    Caption := 'Наименование голоса звукового движка';
    Left := lblName.Left;
    Top := cbMicrophones.Top + cbMicrophones.Height + 10;
    Width := ScaleX(250);
    Height := ScaleY(13);
    Font.Style := [fsBold];
  end;

  cbVoices := TComboBox.Create(Page);
  with cbVoices do
  begin
    Name := 'cbVoices';
    Parent := Page.Surface;
    Left := lblName.Left;
    Top := lblSpeechName.Top + lblSpeechName.Height + 5;
    Width := ScaleX(401);
    Height := ScaleY(21);
    Color := TColor($FFFFFF);
    TabOrder := 5;
    Items.LoadFromFile(ExpandConstant('{tmp}\voices.txt.1251'));
    Style := csDropDownList;
  end;

  VoiceIndex := -1;
  VoiceName := GetIniString('engine', 'SPEECH_ENGINE_RU_NAME', 'Arina', sIniFile);
  
  for i:=0 to cbVoices.Items.Count-1 do
    if VoiceName = cbVoices.Items[i] then
    begin
      VoiceIndex := i;
      break;
    end;
    
  if VoiceIndex <> -1 then
  begin
    cbVoices.ItemIndex := VoiceIndex;
  end else
  begin    
    cbVoices.Items.Insert(0, VoiceName);
    cbVoices.ItemIndex := 0;
    VoiceIndex := 0;
  end;

  { Speech rate }
  lblSpeechRate := Tlabel.Create(Page);
  with lblSpeechRate do
  begin
    Parent := Page.Surface;
    Caption := 'Скорость речи робота';
    Left := lblName.Left;
    Top := cbVoices.Top + cbVoices.Height + 10;
    Width := ScaleX(250);
    Height := ScaleY(13);
    Font.Style := [fsBold];
  end;

  edSpeechRate := TEdit.Create(Page);
  with edSpeechRate do
  begin
    Name := 'edSpeechRate';
    Parent := Page.Surface;
    Left := lblName.Left;
    Top := lblSpeechRate.Top + lblSpeechRate.Height + 5;
    Width := ScaleX(401);
    Height := ScaleY(21);
    Color := TColor($FFFFFF);
    TabOrder := 3;
    Text := IntToStr(GetIniInt('engine', 'SPEECH_RATE_RU', 165, 50, 1000, sIniFile));
  end;

  with Page do
  begin
    OnActivate := @Options1PageActivate;
    OnNextButtonClick := @Options1PageNextButtonClick;
    OnCancelButtonClick := @Options1PageCancel;
  end;
  
  Result := Page.ID;
end;

function CreateOptions2Page(const AfterID: Integer; const IsMPVInstall: Boolean): Integer;
var
  Page: TWizardPage;
  
  lblMPVPath: TLabel;
  edMPVPath: TEdit;
  lblAIMPPath: TLabel;
  edAIMPPath: TEdit;
  lblBooksLibraryPath: TLabel;
  edBooksLibraryPath: TEdit;

  btnGetMPVPath: TButton;
  btnGetAIMPPath: TButton;
  btnGetLibraryPath: TButton;  

  sIniFile: String;
  sMPVAppPath: String;
  sAIMPPath: String;
  sBooksLibraryPath: String;
begin
  sIniFile := ExpandConstant('{tmp}\config.ini.1251');

  if IsMPVInstall then
  begin
    sMPVAppPath := ExpandConstant('{app}\tools\mpv\mpv');
  end else 
  begin
    sMPVAppPath := 'mpv';
    sMPVAppPath := GetIniString('app', 'MPV_APP_PATH', sMPVAppPath, sIniFile);
  end;

  sAIMPPath := GetIniString('app', 'AIMP_PATH', 'C:\\Program Files (x86)\\AIMP\\AIMP.exe', sIniFile);
  sBooksLibraryPath := GetIniString('reading', 'EXTERNAL_LIBRARY_OF_BOOKS_PATH', '', sIniFile);

  StringChangeEx(sMPVAppPath, '\\', '\', True);
  StringChangeEx(sAIMPPath, '\\', '\', True);
  StringChangeEx(sBooksLibraryPath, '\\', '\', True);

  Page := CreateCustomPage(
    AfterID, 
    ExpandConstant('{cm:OptionsPageName}'), 
    ExpandConstant('{cm:OptionsPageDescription}'));

  { MPV player path}
  lblMPVPath := Tlabel.Create(Page);
  with lblMPVPath do
  begin
    Parent := Page.Surface;
    Caption := 'Путь к плееру MPV';
    Left := ScaleX(8);
    Top := ScaleY(3);
    Width := ScaleX(250);
    Height := ScaleY(13);
    Font.Style := [fsBold];
    Font.Color := TColor($800080);
  end;

  edMPVPath := TEdit.Create(Page);
  with edMPVPath do
  begin
    Name := 'edMPVPath';
    Parent := Page.Surface;
    Left := lblMPVPath.Left;
    Top := lblMPVPath.Top + lblMPVPath.Height + 5;
    Width := ScaleX(331);
    Height := ScaleY(21);
    Color := TColor($FFFFFF);
    TabOrder := 1;
    Text := sMPVAppPath;
  end;

  { Get MPV application path }
  btnGetMPVPath := TButton.Create(Page);
  with btnGetMPVPath do
  begin
    Caption := 'Выбрать';
    Parent := Page.Surface;
    Left := edMPVPath.Left + edMPVPath.Width + 5;
    Top := edMPVPath.Top;
    Width := WizardForm.CalculateButtonWidth([Caption]);
    Height := edMPVPath.Height;
    OnClick := @GetMPVPathOnClick;
  end;
  
  { AIMP player path}
  lblAIMPPath := Tlabel.Create(Page);
  with lblAIMPPath do
  begin
    Parent := Page.Surface;
    Caption := 'Путь к плееру AIMP';
    Left := lblMPVPath.Left;
    Top := edMPVPath.Top + edMPVPath.Height + 10;
    Width := ScaleX(250);
    Height := ScaleY(13);
  end;

  edAIMPPath := TEdit.Create(Page);
  with edAIMPPath do
  begin
    Name := 'edAIMPPath';
    Parent := Page.Surface;
    Left := lblMPVPath.Left;
    Top := lblAIMPPath.Top + lblAIMPPath.Height + 5;
    Width := ScaleX(331);
    Height := ScaleY(21);
    Color := TColor($FFFFFF);
    TabOrder := 2;
    Text := sAIMPPath;
  end;

  { Get AIMP application path }
  btnGetAIMPPath := TButton.Create(Page);
  with btnGetAIMPPath do
  begin
    Caption := 'Выбрать';
    Parent := Page.Surface;
    Left := edAIMPPath.Left + edAIMPPath.Width + 5;
    Top := edAIMPPath.Top;
    Width := WizardForm.CalculateButtonWidth([Caption]);
    Height := edAIMPPath.Height;
    OnClick := @GetAIMPPathOnClick;
  end;

  { Books library path }
  lblBooksLibraryPath := Tlabel.Create(Page);
  with lblBooksLibraryPath do
  begin
    Parent := Page.Surface;
    Caption := 'Путь к внешней библиотеке книг на диске';
    Left := lblMPVPath.Left;
    Top := edAIMPPath.Top + edAIMPPath.Height + 10;
    Width := ScaleX(250);
    Height := ScaleY(13);
  end;

  edBooksLibraryPath := TEdit.Create(Page);
  with edBooksLibraryPath do
  begin
    Name := 'edBooksLibraryPath';
    Parent := Page.Surface;
    Left := lblMPVPath.Left;
    Top := lblBooksLibraryPath.Top + lblBooksLibraryPath.Height + 5;
    Width := ScaleX(331);
    Height := ScaleY(21);
    Color := TColor($FFFFFF);
    TabOrder := 3;
    Text := sBooksLibraryPath;
  end;

  { Get Books external Library folder path }
  btnGetLibraryPath := TButton.Create(Page);
  with btnGetLibraryPath do
  begin
    Caption := 'Выбрать';
    Parent := Page.Surface;
    Left := edBooksLibraryPath.Left + edBooksLibraryPath.Width + 5;
    Top := edBooksLibraryPath.Top;
    Width := WizardForm.CalculateButtonWidth([Caption]);
    Height := edBooksLibraryPath.Height;
    OnClick := @GetLibraryPathOnClick;
  end;

  with Page do
  begin
    OnActivate := @Options2PageActivate;
    OnNextButtonClick := @Options2PageNextButtonClick;
    OnCancelButtonClick := @Options2PageCancel;
  end;
  
  Result := Page.ID;
end;

//== end Форма установки параметров ===========================================
//=============================================================================
