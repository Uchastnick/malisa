@echo off
set SCRIPT_DIR=%~dp0
set VENV_SCRIPTS_DIR_FULL_PATH=%SCRIPT_DIR%..\.venv\Scripts\

%VENV_SCRIPTS_DIR_FULL_PATH%python "%SCRIPT_DIR%..\malisa.py" --clock-alarm
