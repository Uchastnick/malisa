#!/bin/sh

SCRIPT_DIR=`pwd`
VENV_SCRIPTS_DIR_FULL_PATH=${SCRIPT_DIR}/../.venv/bin/

PATCH_DIR=${SCRIPT_DIR}/../patch
LIB_DIR=${SCRIPT_DIR%}/../.venv/Lib/site-packages

python -m venv ${SCRIPT_DIR}/../.venv
${VENV_SCRIPTS_DIR_FULL_PATH}python -m pip install -U -r "${SCRIPT_DIR}/../requirements.txt"

cp -r "${PATCH_DIR}/config_to_object/" "${LIB_DIR}"
cp -r "${PATCH_DIR}/speechd/" "${LIB_DIR}"
