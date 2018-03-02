#!/bin/bash
#
# File : loggers.sh
#
# run with applog:
#   $ sudo loggers.sh status|restart|start|stop|forcestop|debug
#
# run without applog:
#   $ loggers.sh status|restart|start|stop|forcestop|debug
#
# init created: 2017-12-09
# last updated: 2018-03-02
#
# find files modified in last 1 miniute
#   $ find ${path} -type f -mmin 1 -exec ls -l {} \;
########################################################################
_file=$(readlink -f $0)
_cdir=$(dirname $_file)
_name=$(basename $_file)

SERVICE_NAME=logger
SERVICE_MODULE=ctls_galaxy_loggers.py
SCRIPTS_USER=root

SCRIPTS_DIR=$(dirname $_cdir)

# Configurations can be changed!
#
LOGLEVEL=INFO
STASHDIR=/var/log/galaxy/

usage() {
    echo "Usage: $_name {debug|start|stop|forcestop|status|restart}"
}


trace() {
    echo "  * scripts dir:  "${SCRIPTS_DIR}
}


debug() {
    echo "Starting ${SERVICE_NAME} as debug mode ..."

    trace 'DEBUG'

    ${SCRIPTS_DIR}/${SERVICE_MODULE} --startup --force --log-level=DEBUG

    echo "* done."
}


start() {
    echo "Starting ${SERVICE_NAME} as user '${SCRIPTS_USER}' ..."

    c_pid=`ps -ef | grep ${SERVICE_MODULE} | grep -v ' grep ' | awk '{print $2}'`

    OLD_IFS="$IFS"
    IFS="\n"
    pids=($c_pid)
    IFS="$OLD_IFS"

    if [ ${#pids[@]} = 0 ]; then
        trace ${LOGLEVEL}

        nohup ${SCRIPTS_DIR}/${SERVICE_MODULE} --startup --force --log-level=${LOGLEVEL}>/dev/null 2>&1 &

        #nohup ${SCRIPTS_DIR}/${SERVICE_MODULE} --startup --force --log-level=${LOGLEVEL} --stash=${STASHDIR}>/dev/null 2>&1 &

        echo "* done."
    else
        for pid in ${pids[@]}
        do
            echo "* ${SERVICE_NAME} ($pid) is already running."
        done
    fi
}


stop() {
    echo "Force stopping ${SERVICE_NAME} ..."

    c_pid=`ps -ef | grep ${SERVICE_MODULE} | grep -v ' grep ' | awk '{print $2}'`

    OLD_IFS="$IFS"
    IFS="\n"
    pids=($c_pid)
    IFS="$OLD_IFS"

    if [ ${#pids[@]} = 0 ]; then
        echo "* ${SERVICE_NAME} not running (stopped)"
    else
        for pid in ${pids[@]}
        do
            echo $pid | xargs kill -9
            echo "* ${SERVICE_NAME} ($pid) force stopped."
        done
    fi

    echo "TODO: Clear zombie processed ..."
    c_pid=`ps -ef|grep ${SERVICE_MODULE} | grep -v ' grep '|awk '{print $2,$9}'`

    echo "$c_pid"
}


forcestop() {
    echo "Force stopping ${SERVICE_NAME} ..."

    c_pid=`ps -ef | grep ${SERVICE_MODULE} | grep -v ' grep ' | awk '{print $2}'`

    OLD_IFS="$IFS"
    IFS="\n"
    pids=($c_pid)
    IFS="$OLD_IFS"

    if [ ${#pids[@]} = 0 ]; then
        echo "* ${SERVICE_NAME} not running (stopped)"
    else
        for pid in ${pids[@]}
        do
            echo $pid | xargs kill -9
            echo "* ${SERVICE_NAME} ($pid) force stopped."
        done
    fi

    echo "TODO: Clear zombie processed ..."
    c_pid=`ps -ef|grep ${SERVICE_MODULE} | grep -v ' grep '|awk '{print $2,$9}'`

    echo "$c_pid"
}


status() {
    c_pid=`ps -ef | grep ${SERVICE_MODULE} | grep -v ' grep ' | awk '{print $2}'`

    OLD_IFS="$IFS"
    IFS="\n"
    pids=($c_pid)
    IFS="$OLD_IFS"

    if [ ${#pids[@]} = 0 ]; then
        echo "* ${SERVICE_NAME} not running (stopped)"
    else
        for pid in ${pids[@]}
        do
            echo "* ${SERVICE_NAME} ($pid) is running with opened descriptors:"
            lsof -p $pid -n|awk '{print $2}'|sort|uniq -c|sort -nr|more
        done
    fi
}


# See how we were called.
case "$1" in
    debug)
        debug
        exit 0
    ;;

    start)
       start
       exit 0
    ;;

    stop)
       stop
       exit 0
    ;;

    forcestop)
        forcestop
        exit 0
    ;;

    status)
        status
        exit 0
    ;;

    restart)
        stop
        start
        exit 0
    ;;

    *)
        usage
        exit 0
    ;;

esac
