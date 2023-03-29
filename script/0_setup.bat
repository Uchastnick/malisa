@echo off
set SCRIPT_DIR=%~dp0
set VENV_SCRIPTS_DIR_FULL_PATH=%SCRIPT_DIR%..\.venv\Scripts\

set PATCH_DIR=%SCRIPT_DIR%..\patch
set LIB_DIR=%SCRIPT_DIR%..\.venv\Lib\site-packages

set DATA_DIR=%SCRIPT_DIR%..\data
set TMP_DIR=%SCRIPT_DIR%..\tmp

:: --- Создание виртуального окружения и настройка библиотек ---

python -m venv "%SCRIPT_DIR%..\.venv"
%VENV_SCRIPTS_DIR_FULL_PATH%pip install -U -r "%SCRIPT_DIR%..\requirements.txt"

:: --- Патчи библиотек ---

xcopy /y /s /e /i "%PATCH_DIR%\config_to_object" "%LIB_DIR%\config_to_object"
xcopy /y /s /e /i "%PATCH_DIR%\speechd" "%LIB_DIR%\speechd"

:: --- Загрузка и распаковка моделей локального распознавания речи ---

set VOSK_MODELS_URL=https://alphacephei.com/vosk/models

set MODEL_RU=vosk-model-small-ru-0.22
set MODEL_EN=vosk-model-small-en-us-0.15
set MODEL_DE=vosk-model-small-de-0.15

curl %VOSK_MODELS_URL%/%MODEL_RU%.zip -L -k -o %TMP_DIR%\%MODEL_RU%.zip
:: -- Будет доступно в последующих версиях --
::curl %VOSK_MODELS_URL%/%MODEL_EN%.zip -L -k -o %TMP_DIR%\%MODEL_EN%.zip
::curl %VOSK_MODELS_URL%/%MODEL_DE%.zip -L -k -o %TMP_DIR%\%MODEL_DE%.zip

cd %TMP_DIR%

7z x -y %MODEL_RU%.zip
:: -- Будет доступно в последующих версиях --
::7z x -y %MODEL_EN%.zip
::7z x -y %MODEL_DE%.zip

move /y %MODEL_RU% "%DATA_DIR%\vosk-model-small-ru"
:: -- Будет доступно в последующих версиях --
mkdir "%DATA_DIR%\vosk-model-small-en"
mkdir "%DATA_DIR%\vosk-model-small-de"
::move /y %MODEL_EN% "%DATA_DIR%\vosk-model-small-en"
::move /y %MODEL_DE% "%DATA_DIR%\vosk-model-small-de"

del /q /f %MODEL_RU%.zip
del /q /f %MODEL_EN%.zip
del /q /f %MODEL_DE%.zip

cd %SCRIPT_DIR%
