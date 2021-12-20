@echo off
set SCRIPT_DIR=%~dp0
pip install "%SCRIPT_DIR%..\_distr\PyAudio-0.2.11-cp37-cp37m-win_amd32.whl"
pip install -r "%SCRIPT_DIR%..\requirements.txt"
