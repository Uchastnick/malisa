@echo off
set SCRIPT_DIR=%~dp0
set VENV_SCRIPTS_DIR_FULL_PATH=%SCRIPT_DIR%..\.venv\Scripts\

python -m venv "%SCRIPT_DIR%..\.venv"
%VENV_SCRIPTS_DIR_FULL_PATH%pip install -U -r "%SCRIPT_DIR%..\requirements.txt"
