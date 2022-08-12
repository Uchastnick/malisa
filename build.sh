#!/bin/sh

SCRIPT_DIR=`pwd`
VENV_SCRIPTS_DIR_FULL_PATH="${SCRIPT_DIR}/.venv/bin/"

BASENAME=malisa
RELEASE_DIR=_release

PYTHON_VER=cp310
OS_VER=x86_64-linux

BUILD_DIR=./${RELEASE_DIR}/build
DIST_DIR=./${RELEASE_DIR}/dist
LIB_DIR=${DIST_DIR}/${BASENAME}/lib-dynload

ARCHIVE_FILE=${DIST_DIR}/${BASENAME}-${PYTHON_VER}-${OS_VER}.zip

${VENV_SCRIPTS_DIR_FULL_PATH}pyinstaller -y --clean --distpath "${DIST_DIR}" --workpath "${BUILD_DIR}" ${BASENAME}.spec
mkdir "${LIB_DIR}"

mv -v ${DIST_DIR}/${BASENAME}/*.* ${LIB_DIR}
mv -v ${LIB_DIR}/*.md ${LIB_DIR}/*.bat ${LIB_DIR}/*.sh ${DIST_DIR}/${BASENAME}
mv -v ${LIB_DIR}/libpython3*.so* ${LIB_DIR}/base_library.zip ${DIST_DIR}/${BASENAME}

rm -v ${DIST_DIR}/${BASENAME}/*.bat
rm -v ${DIST_DIR}/${BASENAME}/_dist/*.zip
rm -v ${ARCHIVE_FILE}

7z a -tzip -r0 ${ARCHIVE_FILE} ${DIST_DIR}/${BASENAME}

printf "Ok\n"
