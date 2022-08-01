:: Автозагрузка => shell:startup
@echo off
::timeout.exe /t 150
cls
set SCRIPT_DIR=%~dp0
"%SCRIPT_DIR%..\malisa.exe"
