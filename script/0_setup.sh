#!/bin/sh

SCRIPT_DIR=`pwd`
VENV_SCRIPTS_DIR_FULL_PATH=${SCRIPT_DIR}/../.venv/bin/

PYTHON_VERSION=python3.10

PATCH_DIR=${SCRIPT_DIR}/../patch
LIB_DIR=${SCRIPT_DIR%}/../.venv/lib/${PYTHON_VERSION}/site-packages

# --- Создание виртуального окружения и настройка библиотек ---

python -m venv ${SCRIPT_DIR}/../.venv

. ${SCRIPT_DIR}/../.venv/bin/activate
#${VENV_SCRIPTS_DIR_FULL_PATH}python -m pip install -U -r "${SCRIPT_DIR}/../requirements.txt"
python -m pip install -U -r "${SCRIPT_DIR}/../requirements.txt"

# --- Патчи библиотек ---

cp -r "${PATCH_DIR}/config_to_object/" "${LIB_DIR}"
cp -r "${PATCH_DIR}/speechd/" "${LIB_DIR}"

# --- Загрузка и распаковка моделей локального распознавания речи ---

VOSK_MODELS_URL=https://alphacephei.com/vosk/models

MODEL_RU=vosk-model-small-ru-0.22
MODEL_EN=vosk-model-small-en-us-0.15
MODEL_DE=vosk-model-small-de-0.15

