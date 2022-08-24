#!/bin/sh

SCRIPT_DIR=`pwd`
VENV_SCRIPTS_DIR_FULL_PATH=${SCRIPT_DIR}/../.venv/bin/

PYTHON_VERSION=python3.10

PATCH_DIR=${SCRIPT_DIR}/../patch
LIB_DIR=${SCRIPT_DIR%}/../.venv/lib/${PYTHON_VERSION}/site-packages

python -m venv ${SCRIPT_DIR}/../.venv

. ${SCRIPT_DIR}/../.venv/bin/activate
#${VENV_SCRIPTS_DIR_FULL_PATH}python -m pip install -U -r "${SCRIPT_DIR}/../requirements.txt"
python -m pip install -U -r "${SCRIPT_DIR}/../requirements.txt"

cp -r "${PATCH_DIR}/config_to_object/" "${LIB_DIR}"
cp -r "${PATCH_DIR}/speechd/" "${LIB_DIR}"
