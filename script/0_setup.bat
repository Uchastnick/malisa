@echo off
set SCRIPT_DIR=%~dp0
set VENV_SCRIPTS_DIR_FULL_PATH=%SCRIPT_DIR%..\.venv\Scripts\

set PATCH_DIR=%SCRIPT_DIR%..\patch
set LIB_DIR=%SCRIPT_DIR%..\.venv\Lib\site-packages

python -m venv "%SCRIPT_DIR%..\.venv"
%VENV_SCRIPTS_DIR_FULL_PATH%pip install -U -r "%SCRIPT_DIR%..\requirements.txt"

xcopy /y /s /e /i "%PATCH_DIR%\config_to_object" "%LIB_DIR%\config_to_object"
xcopy /y /s /e /i "%PATCH_DIR%\speechd" "%LIB_DIR%\speechd"
