@echo off
set SCRIPT_DIR=%~dp0
set VENV_SCRIPTS_DIR_FULL_PATH=%SCRIPT_DIR%\.venv\Scripts\

set BASENAME=malisa
set RELEASE_DIR=_release

set PYTHON_VER=cp37
set OS_VER=win7_amd64

set BUILD_DIR=./%RELEASE_DIR%/build
set DIST_DIR=./%RELEASE_DIR%/dist
set LIB_DIR=%DIST_DIR%/%BASENAME%/lib-dynload

set ARCHIVE_FILE=%DIST_DIR%\%BASENAME%-%PYTHON_VER%-%OS_VER%.zip

%VENV_SCRIPTS_DIR_FULL_PATH%pyinstaller -y --clean --distpath "%DIST_DIR%" --workpath "%BUILD_DIR%" %BASENAME%.spec
mkdir "%LIB_DIR%"

move %DIST_DIR%\%BASENAME%\*.pyd "%LIB_DIR%"
move %DIST_DIR%\%BASENAME%\*.dll "%LIB_DIR%"
move %LIB_DIR%\python3*.dll "%DIST_DIR%\%BASENAME%"

move %DIST_DIR%\%BASENAME%\script\%BASENAME%_local.bat %DIST_DIR%\%BASENAME%\%BASENAME%.bat
del "%ARCHIVE_FILE%"

7z a -tzip -r0 %ARCHIVE_FILE% %DIST_DIR%\%BASENAME%

echo Ok
