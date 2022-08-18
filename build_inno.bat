@echo off
set SCRIPT_DIR=%~dp0

set BASENAME=malisa
set RELEASE_DIR=_release

set VERSION=
for /f "usebackq tokens=* delims=" %%i in (".\VERSION") do set VERSION=%%i

set PYTHON_VER=cp37
set OS_VER=win-amd64

set INNO_SCRIPT="%SCRIPT_DIR%\inno\%BASENAME%.iss"

::set BUILD_TOOL="C:\Program Files (x86)\Inno Script Studio\ISStudio.exe"
set BUILD_TOOL="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

::%BUILD_TOOL% -compile %INNO_SCRIPT%
%BUILD_TOOL% /O+ "/DMyAppVersion=%VERSION%" "/DPythonVersion=%PYTHON_VER%" "/DWinVersion=%OS_VER%" %INNO_SCRIPT%

move /y "%SCRIPT_DIR%\inno\%RELEASE_DIR%\*.exe" "%SCRIPT_DIR%\%RELEASE_DIR%"

echo Build Inno - Ok
