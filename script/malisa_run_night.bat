:: Автозагрузка => shell:startup
@echo off
::timeout.exe /t 150
cls
set SCRIPT_DIR=%~dp0
set VENV_SCRIPTS_DIR_FULL_PATH=%SCRIPT_DIR%..\.venv\Scripts\

%VENV_SCRIPTS_DIR_FULL_PATH%python "%SCRIPT_DIR%..\malisa.py" --nightmode
