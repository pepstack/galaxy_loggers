#!/bin/bash
#
# File : clean.sh
#
# init created: 2016-05-27
# last updated: 2017-12-11
#
########################################################################
_file=$(readlink -f $0)
_cdir=$(dirname $_file)
_name=$(basename $_file)

PREFIX=$(dirname $_cdir)

# remove .pyc from below dirs:
SRC_DIR=${PREFIX}
UTILS_DIR=${PREFIX}/utils
LOGGERS_DIR=${PREFIX}/loggers

# remove .log from below dir:
APPLOG_DIR=${PREFIX}/applog

# remove services from below dir:
SERVICE_DIR=${PREFIX}/service

###################################################
echo "**** clean files (*.pyc) in ${SRC_DIR}"
find ${SRC_DIR} -name *.pyc | xargs rm -f

echo "**** clean files (*.pyc) in ${UTILS_DIR}"
find ${UTILS_DIR} -name *.pyc | xargs rm -f

echo "**** clean files (*.pyc) in ${LOGGERS_DIR}"
find ${LOGGERS_DIR} -name *.pyc | xargs rm -f


echo "**** clean files (*.log, *.lock) in ${APPLOG_DIR}"
find ${APPLOG_DIR} -name *.log | xargs rm -f
find ${APPLOG_DIR} -name *.lock | xargs rm -f

echo "**** remove 'supervise' in ${SERVICE_DIR}"
find ${SERVICE_DIR} -name 'supervise' | xargs rm -rf

echo "**** clean all ok."
