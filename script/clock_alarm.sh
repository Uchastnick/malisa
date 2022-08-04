#!/bin/sh

SCRIPT_DIR=`pwd`
VENV_SCRIPTS_DIR_FULL_PATH="${SCRIPT_DIR}/../.venv/bin/"

${VENV_SCRIPTS_DIR_FULL_PATH}python "${SCRIPT_DIR}/../malisa.py" --clock-alarm
