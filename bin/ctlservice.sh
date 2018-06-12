#!/bin/bash
# @file: ctlservice.sh
#
#   java 服务控制脚本, 控制 jar 服务的启动, 关闭, 状态查询等
#
#     $ ./ctlservice.sh start|stop
#
# @author: master@pepstack.com
#
# @create: 2018-06-08
#
# @update: 2018-06-12 14:15:35
#
########################################################################
# NOTE: readlink -f not support by MaxOS-X
_file=$(readlink -f $0)
_cdir=$(dirname $_file)
_name=$(basename $_file)

_ver=0.0.1

# 单例运行(=1)
_maxservs=1

# 停止等待秒
_stopwait=1s

_loglevel=DEBUG


. $_cdir/common.sh

# Set characters encodeing
#   LANG=en_US.UTF-8;export LANG
LANG=zh_CN.UTF-8;export LANG
########################################################################
# 最多服务实例数: 1 (单例服务)
maxservs=$_maxservs

# 关闭等待超时
stopwait=$_stopwait


# 取得祖父目录名所为默认服务名
def_servname=$(basename $(dirname $_cdir))".py"

# is script in bin dir?
if [ "$(basename $_cdir)" == " bin" ]; then
    echoerror "脚本所在目录不是 bin 目录: $_cdir"
    exit -1
fi

# Treat unset variables as an error
set -o nounset

########################################################################

#------------------------------------------------
# FUNCTION: usage
# DESCRIPTION:  Display usage information.
#------------------------------------------------
usage() {
    cat << EOT

    用法:  ${_name} [Options] Command

        java 服务控制脚本, 控制 jar 服务的启动(start), 停止(stop), 状态(status)等.

    Options:
        -h, --help                  显示帮助
        -V, --version               显示版本

        -u,--runuser=USER           控制服务的用户. 默认 root
        -s,--service=SERV           服务的主模块名
        -l,--loglevel=LEVEL         服务的日志水平: DEBUG|INFO|WARN|ERROR. 默认 DEBUG

    Command:
        start                       启动服务
        stop                        停止服务
        status                      服务状态
        kill                        强迫中止服务
        debug                       调试运行
        restart                     重启服务

    返回值:
        0      成功
        非 0   失败

    示例:
        1) 以用户 root1 启动服务
            # {_name} -u root1 start

        2) 关闭服务
            # {_name} stop

    报告错误: 350137278@qq.com
EOT
}   # ----------  end of function usage  ----------

if [ $# -eq 0 ]; then usage; exit 1; fi

# check user if root
uname=`id -un`

# parse options:
RET=`getopt -o Vhu:s:l: --long version,help,runuser:,service:,loglevel:, \
    -n ' * ERROR' -- "$@"`

if [ $? != 0 ] ; then echoerror "$_name exited with doing nothing." >&2 ; exit 1 ; fi

# Note the quotes around $RET: they are essential!
eval set -- "$RET"

# 控制命令
ctlcommand=

# 运行的用户
rununame=

# 服务名
servname=

# 日志记录水平
loglevel=$_loglevel


# set option values
while true; do
    case "$1" in
        -V | --version) echoinfo "$(basename $0) -- version: $_ver"; exit 1;;
        -h | --help ) usage; exit 1;;

        -u | --runuser ) rununame="$2"; shift 2 ;;

        -s | --service ) servname="$2"; shift 2 ;;
        
        -l | --loglevel ) loglevel="$2"; shift 2 ;;

        -- ) if [ $# -eq 2 ]; then ctlcommand="$2"; fi; shift; break ;;

        * ) break ;;
    esac
done


# check inputs
if [ -z "$servname" ]; then
    echowarn "未指定服务 py. 默认使用: $def_servname"
    servname=$def_servname
fi


# check inputs
if [ -z "$rununame" ]; then
    echowarn "未指定运行的用户. 默认用户: $uname"
    rununame=$uname
fi

# check inputs
if [ -z "$ctlcommand" ]; then
    echoerror "未指定命令. 可用的命令: start|stop|status|forcestop|debug|restart"
    exit 1
fi

servmodule="$_cdir"/"$servname"

# 服务模块文件是否存在
#   服务模块必须在当前路径下(或者是符号链接)
#
if [ ! -f "$servmodule" ]; then
    echoerror "服务模块文件或服务模块的符号链接文件未发现: $servmodule"
    exit 1
fi

# 取得模块真实物理位置
real_servmodule=$(readlink -f $servmodule)

if [ "$real_servmodule" == "$servmodule" ]; then
    echoinfo "服务模块: "$servmodule
else
    echoinfo "服务模块: "$servmodule" =>"
    echoinfo " => "$real_servmodule
fi

echoinfo "当前登录用户: "$uname
echoinfo "运行命令用户: "$rununame
echoinfo "命令: "$ctlcommand

status() {
    # 显示服务的状态： 进程 pid, 进程打开的文件句柄数 ofd
    echoinfo "服务状态: $servname - $servmodule"

    local pids=$(pids_of_proc "$servmodule")

    local i=0
    local total_ofd=0

    if [ -z "$pids" ]; then
        echo -e "    未发现服务: ${RC}$servname${EC}"
    else
        for pid in ${pids[@]}
        do
            let i=i+1

            # pid 进程打开的文件句柄数 ofd
            local ofd=$(openfd_of_pid "$pid")
            let total_ofd=total_ofd+ofd
            echo -e "    [$i] 正在运行 ${GC}$servname${EC} (pid = ${GC}$pid${EC}, ofd = ${GC}$ofd${EC})"
        done
    fi

    echowarn "TODO: 清理查看僵尸进程"
    #ps -ef|grep ${servmodule} | grep -v ' grep '|awk '{print $2,$9}'

    echowarn "$i 个服务进程正在运行, 总计打开的文件描述符: $total_ofd."

    return $i
}


debug() {
    # 提示用户确认
    read -p "以调试模式启动服务: $servname. 确认(Y|yes)? : "

    # 去掉多余空格
    RET=${REPLY//[[:space:]]/}

    if [ "$RET" != "Y" ] && [ "$RET" != "yes" ]; then
        echowarn "用户取消了操作！"
        exit -1
    fi

    echoinfo "开始启动服务 ..."

    if [ "$uname" == "$rununame" ]; then
        echowarn "当前登录用户与运行用户相同, 未使用 runuser"
        "$servmodule" --startup --force --log-level=$loglevel        
    elif [ "$uname" == "root" ]; then
        runuser - "$rununame" -c ''"$servmodule"' --startup --force --log-level=$loglevel'
    else
        echoerror "请用 root 用户运行 runuser !"
    fi

    echoinfo "服务已中止."
}


start() {
    # 启动服务, 如果发现服务已经运行, 启动失败

    local pids=$(pids_of_proc "$servmodule")

    # 正在运行的服务实例数
    local num=0
    if [ ! -z "$pids" ]; then
        for pid in ${pids[@]}
        do
            let num=num+1
        done
    fi

    if [ "$num" -ge "$maxservs" ]; then
        echoerror "已经达到服务实例上限(maxservs=$maxservs)."
        exit -1
    fi

    echoinfo "开始启动后台服务 ..."

    if [ "$uname" == "$rununame" ]; then
        echowarn "当前登录用户与运行用户相同, 未使用 runuser"
        nohup "$servmodule" --startup --force --log-level=$loglevel > /dev/null 2>&1 &
    elif [ "$uname" == "root" ]; then
        runuser - "$rununame" -c ''"$servmodule"' --startup --force --log-level=$loglevel > /dev/null 2>&1 &'
    else
        echoerror "请用 root 用户运行 runuser !"
    fi

    echoinfo "服务已经启动. 服务状态查看命令: status"
}


stop() {
    local pids=$(pids_of_proc "$servmodule")

    if [ -z "$pids" ]; then
        echowarn "未发现服务实例: $servname"
    else
        # 强行杀死服务进程
        for pid in ${pids[@]}
        do
            echowarn "正在关闭 $servname (pid=$pid) ..."

            echo $pid | xargs kill

            sleep "$stopwait"
        done

        # 确认服务已经关闭
        local dpids=$(pids_of_proc "$servmodule")

        if [ -z "$dpids" ]; then
            echoinfo "服务已成功关闭: $servname"
        else
            echowarn "无法关闭服务: $servname. 使用 forcestop 命令重试!"
        fi
    fi
}


forcestop() {
    # 先优雅关闭
    stop

    local pids=$(pids_of_proc "$servmodule")

    if [ -z "$pids" ]; then
        echowarn "服务已中止."
    else
        # 强行杀死服务进程
        for pid in ${pids[@]}
        do
            echo $pid | xargs kill -9
            echowarn "pid=$pid killed"
        done

        echowarn "服务已强迫中止."
    fi
}


if [ "$ctlcommand" == "debug" ]; then
    debug
elif [ "$ctlcommand" == "start" ]; then
    start
elif [ "$ctlcommand" == "stop" ]; then
    stop
elif [ "$ctlcommand" == "kill" ]; then
    forcestop
elif [ "$ctlcommand" == "forcestop" ]; then
    forcestop
elif [ "$ctlcommand" == "status" ]; then
    status
elif [ "$ctlcommand" == "restart" ]; then
    forcestop
    start
else
    echoerror "不能识别的命令."
    exit -1
fi

exit 0
