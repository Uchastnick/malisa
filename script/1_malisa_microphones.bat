@echo off
cls
set SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%..\malisa.py" --microphones
pause
