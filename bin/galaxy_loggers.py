#!/usr/bin/python
#-*- coding: UTF-8 -*-
#
# galaxy_loggers-2.0.0.py
#
#   生成测试数据文件
#
#   see: $APPHELP
#
# ZhangLiang, 350137278@qq.com
#
# LOGS:
#   -- 2017-12-08: first created
#   -- 2018-03-02: last updated and released
########################################################################
import os, sys, signal, shutil, inspect, commands
import importlib
import time, datetime
import optparse, ConfigParser

import multiprocessing, threading
from multiprocessing import Process, Queue
from Queue import Empty, Full

########################################################################
# application specific
APPFILE = os.path.realpath(sys.argv[0])
APPHOME = os.path.dirname(APPFILE)
APPNAME,_ = os.path.splitext(os.path.basename(APPFILE))
APPVER = "2.0.0"
APPHELP = "Control Script for producing a mass of test csv files."

########################################################################
# import your local modules
import utils.utility as util
import utils.evntlog as elog

########################################################################
# 用户可以根据系统和需求设置 loggers 进程数: LOGGER_WORKERS_MAX
# 最大 loggers 支持, 可以更改
#
LOGGER_WORKERS_MAX = 200


########################################################################
exit_event, exit_queue = (threading.Event(), Queue(LOGGER_WORKERS_MAX))

# 子进程结束时, 父进程会收到这个信号。
# 如果父进程没有处理这个信号，也没有等待(wait)子进程，子进程虽然终止，
# 但是还会在内核进程表中占有表项，这时的子进程称为僵尸进程。
# 这种情况我们应该避免.
#
#   父进程或者忽略SIGCHILD信号，或者捕捉它，或者wait它派生的子进程，
#   或者父进程先终止，这时子进程的终止自动由init进程来接管
#
def onSigChld(signo, frame):
    global exit_queue, exit_event
    pid, status = os.waitpid(-1, os.WNOHANG)
    if pid:
        elog.error("child#%d on signal: SIGCHLD.", pid)
        exit_queue.put(('EXIT', "child#%d on signal: SIGCHLD." % pid))
        exit_event.set()
    pass


def onSigInt(signo, frame):
    global exit_queue, exit_event
    exit_queue.put(('EXIT', "process#%d on signal: SIGINT." % os.getpid()))
    exit_event.set()
    pass


def onSigTerm(signo, frame):
    global exit_queue, exit_event
    exit_queue.put(('EXIT', "process#%d on signal: SIGTERM." % os.getpid()))
    exit_event.set()
    pass


########################################################################
def load_logger_workers(loggers_dir, workers, loggerConfig):
    loggers = {}
    worker_modules = ["%s.%s" % (loggers_dir, workers[i]) for i in range(0, len(workers))]
    try:
        for worker in worker_modules:
            elog.debug("import %s", worker)
            module = importlib.import_module(worker)
            loggers[worker] = (module, loggerConfig)
            pass
        return loggers
    except ImportError as ie:
        elog.error("%r", ie)
        sys.exit(-1)
        pass


########################################################################
def logger_worker(loggerSet, config, exit_queue, timeout_ms):
    (loggerModule, loggerConfig) = loggerSet

    loggerClass = loggerModule.create_logger_instance(loggerConfig)

    elog.force("worker process(%d) for %s start ...", os.getpid(), loggerClass.logger_name)

    is_exit, exit_arg = (False, None)

    while not is_exit:
        is_exit, exit_arg = util.is_exit_process(exit_queue, timeout_ms)

        if is_exit:
            exit_queue.put(('EXIT', exit_arg))
            break

        loggerModule.log_messages(loggerClass)
        pass
    else:
        elog.fatal("worker process exit: %r", exit_arg)
        pass


########################################################################
def run_forever(processes, exit_event):
    for name, proc in processes.items():
        elog.force("start worker process: %s", name)
        proc.start()

    idle_queue = Queue(1)

    while not exit_event.isSet():
        try:
            func, arg = idle_queue.get(block=True, timeout=3)
        except Empty:
            pass
    else:
        for name, proc in processes.items():
            exit_queue.put(('EXIT', 'main process exit.'))

        for name, proc in processes.items():
            proc.join()

        elog.force("main process exit.")
        pass


########################################################################
# start worker loggers
#
def startup(loggers, config):
    processes = {}

    # 主进程退出信号
    signal.signal(signal.SIGINT, onSigInt)
    signal.signal(signal.SIGTERM, onSigTerm)

    for loggerClassName in loggers:
        elog.force("create process for logger: %s", loggerClassName)

        p = Process(target = logger_worker, args = (loggers[loggerClassName], config, exit_queue, 0.01))
        p.daemon = True
        processes[loggerClassName] = p
        pass

    run_forever(processes, exit_event)
    pass


########################################################################
def list_logger_workers(logConfigDict, workersDir):
    found_workers = []

    for loggerName in logConfigDict['loggers']:
        worker_py = "%s.py" % loggerName
        if worker_py in os.listdir(workersDir):
            found_workers.append(loggerName)
        pass
    found_workers.sort()
    return found_workers


########################################################################
def reset_logger_position(loggers, workersDir, start_time, start_rowid):
    for loggerName in loggers:
        _, worker = os.path.splitext(loggerName)
        position_file = os.path.join(workersDir, "%s.position" % worker)

        st_dt = time.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        start_tstamp = int(time.mktime(st_dt))

        line = "%d,%d\n" % (start_tstamp, start_rowid)
        util.write_first_line_nothrow(position_file, line)

        elog.force("%d ('%s'), %d => position file: %s", start_tstamp, start_time, start_rowid, position_file)
    pass


########################################################################
def add_logger(config, found_workers):
    import yaml
    from copy import deepcopy

    NN = len(found_workers)

    if NN > LOGGER_WORKERS_MAX:
        elog.warn("too many loggers(>%d) to add", LOGGER_WORKERS_MAX)
        return

    loggerPrefix = found_workers[0].split('-')[0]

    newLoggerName = "%s-%d" % (loggerPrefix, NN)
    while newLoggerName in found_workers:
        NN = NN + 1
        newLoggerName = "%s-%d" % (loggerPrefix, NN)

    # add loggerNN:
    logger0 = os.path.join(config['loggers_abspath'], "%s.py" % loggerPrefix)
    loggerNN = os.path.join(config['loggers_abspath'], "%s.py" % newLoggerName)

    elog.info("%s: %s", newLoggerName, loggerNN)

    (fr, fd) = (None, None)
    try:
        loggingConfigYaml = config['logger']['logging_config']
        loggingConfigYamlDefault = "%s.0" % loggingConfigYaml

        shutil.copy(loggingConfigYaml, loggingConfigYamlDefault)

        fr = open(loggingConfigYaml)
        cfg = yaml.load(fr)
        fr.close()
        fr = None

        fd = util.open_file(loggingConfigYaml)

        cfg['loggers'][newLoggerName] = deepcopy(cfg['loggers'][loggerPrefix])

        yaml.dump(cfg, fd, default_flow_style=False)

        fd.close()
        fd = None

        shutil.copy(logger0, loggerNN)

        shutil.copy(loggingConfigYaml, loggingConfigYamlDefault)
        elog.info("success: %s", newLoggerName)
    except:
        shutil.copy(loggingConfigYamlDefault, loggingConfigYaml)
        elog.error("failed: %s", newLoggerName)
        pass
    finally:
        if fr:
            fr.close()
        if fd:
            fd.close()
    pass


########################################################################
def remove_logger(config, found_workers):
    import yaml
    NN = len(found_workers) - 1

    if NN == 0:
        elog.warn("no logger can be removed")
        return

    loggerPrefix = found_workers[0].split('-')[0]

    delLoggerName = "%s-%d" % (loggerPrefix, NN)

    while delLoggerName not in found_workers and NN < LOGGER_WORKERS_MAX:
        NN = NN + 1
        delLoggerName = "%s-%d" % (loggerPrefix, NN)

    if delLoggerName not in found_workers:
        elog.warn("no logger can be removed")
        return

    # remove file loggerNN:
    loggerNN = os.path.join(config['loggers_abspath'], "%s.py" % delLoggerName)
    loggerNNPosition = os.path.join(config['loggers_abspath'], ".%s.position" % delLoggerName)

    elog.info("%s: %s", delLoggerName, loggerNN)

    (fr, fd) = (None, None)
    try:
        loggingConfigYaml = config['logger']['logging_config']
        loggingConfigYamlDefault = "%s.0" % loggingConfigYaml

        shutil.copy(loggingConfigYaml, loggingConfigYamlDefault)

        fr = open(loggingConfigYaml)
        cfg = yaml.load(fr)
        fr.close()
        fr = None

        del cfg['loggers'][delLoggerName]

        fd = util.open_file(loggingConfigYaml)
        yaml.dump(cfg, fd, default_flow_style=False)
        fd.close()
        fd = None

        os.remove(loggerNN)
        os.remove(loggerNNPosition)

        shutil.copy(loggingConfigYaml, loggingConfigYamlDefault)
        elog.info("success: %s", delLoggerName)
    except:
        shutil.copy(loggingConfigYamlDefault, loggingConfigYaml)
        elog.error("failed: %s", delLoggerName)
        pass
    finally:
        if fr:
            fr.close()
        if fd:
            fd.close()
    pass


########################################################################
# main function
#
def main(config, parser):
    import utils.logger as logger

    (options, args) = parser.parse_args(args=None, values=None)

    logConfigDict = logger.set_logger(config['logger'], options.log_path, options.log_level)

    loggers = {}

    if config['loggers'] and len(config['loggers']):
        loggers = load_logger_workers('loggers', config['loggers'], {
                'logger_config' : logConfigDict,
                'logger_stash' : options.logger_stash,
                'batch_rows' : options.batch_rows,
                'end_time' : options.end_time,
                'end_rowid' : options.end_rowid
            })

    if len(loggers) > LOGGER_WORKERS_MAX:
        elog.error("too many logger workers. please increase LOGGER_WORKERS_MAX and try!")
        exit(-1)

    found_workers = list_logger_workers(logConfigDict, config['loggers_abspath'])

    if options.list_logger_workers:
        for logger_worker in found_workers:
            elog.info("found worker: %s (%s/%s.py)", logger_worker, config['loggers_abspath'], logger_worker)
        elog.force("total %d workers: %r", len(found_workers), found_workers)
        return

    if options.add_logger:
        add_logger(config, found_workers)
        return

    if options.remove_logger:
        remove_logger(config, found_workers)
        return

    if len(loggers) == 0 and options.force:
        loggers = load_logger_workers('loggers', found_workers, {
                'logger_config' : logConfigDict,
                'logger_stash' : options.logger_stash,
                'batch_rows' : options.batch_rows,
                'end_time' : options.end_time,
                'end_rowid' : options.end_rowid
            })

    if options.reset_logger_position:
        if len(loggers):
            reset_logger_position(loggers, config['loggers_abspath'], options.start_time, options.start_rowid)
        else:
            elog.error("--reset-position ignored: logger worker not found. use --force for all.")
        pass

    if options.startup:
        if len(loggers):
            startup(loggers, config)
        else:
            elog.error("--startup ignored: logger worker not found. use --force for all.")
        pass

    pass


########################################################################
# Usage:
#  1) 启动 weblogger
#    $ sudo galaxy_loggers.py weblogger --startup
#
#  2) 启动 weblogger, weblogger2
#    $ galaxy_loggers.py weblogger,weblogger2 --startup
#    $ galaxy_loggers.py "weblogger, weblogger2" --startup
#
# 3) 启动所有 logger workers
#    $ galaxy_loggers.py --startup --force
#
# 4) 显示所有 logger workers 列表
#    $ galaxy_loggers.py --list
#
# 5) 重置 weblogger, weblogger2 的位置
#    $ galaxy_loggers.py weblogger,weblogger2 --reset-position
#
# 6) 重置 weblogger 的位置在指定位置
#    $ galaxy_loggers.py weblogger --reset-position --start-time="2000-01-01 00:00:00" --rowid=1000000000000
#
# 7) 重置所有插件的位置在默认位置
#    $ galaxy_loggers.py --reset-position --force
#
# 8) 增加一个 loggerNN, NN 自动计算
#    $ galaxy_loggers.py --add-logger
#
# 9) 删除最后增加的 loggerNN
#    $ galaxy_loggers.py --remove-logger
#
# 10) 显示帮助
#    $ galaxy_loggers.py --help
#
# 注意:
#   如果不是以 root 用户启动程序, 则应用程序本身的日志 (applog) 不会创建.
#
########################################################################
if __name__ == "__main__":

    parser, group, optparse = util.use_parser_group(APPNAME, APPVER, APPHELP,
        '%prog WORKERs [Options] ...\n  WORKERs   names for logger workers. (for instance: "weblogger,webloger2")')

    group.add_option("--log-path",
        action="store", dest="log_path", type="string", default=os.path.join(APPHOME, "applog"),
        help="specify path to store application log (NOT logger data files)",
        metavar="LOGPATH")

    group.add_option("--log-level",
        action="store", dest="log_level", type="string", default="DEBUG",
        help="specify log level for logger: DEBUG, WARN, INFO, ERROR. default: DEBUG",
        metavar="LOGLEVEL")

    # you may change below for override default setting:
    stash_dir = os.path.join(APPHOME, "tmp/stash")

    group.add_option("--stash",
        action="store", dest="logger_stash", type="string", default=stash_dir,
        help="specify stash dir for storing logger data files. '" + stash_dir + "' (default)",
        metavar="STASH")

    group.add_option("--list",
        action="store_true", dest="list_logger_workers", default=False,
        help="list all logger workers")

    group.add_option("--add-logger",
        action="store_true", dest="add_logger", default=False,
        help="add a new logger")

    group.add_option("--remove-logger",
        action="store_true", dest="remove_logger", default=False,
        help="remove the last added logger")

    group.add_option("--reset-position",
        action="store_true", dest="reset_logger_position", default=False,
        help="reset given worker's position")

    group.add_option("--start-time",
        action="store", dest="start_time", type="string", default="2000-01-01 00:00:00",
        help="reset given worker's start time. '2000-01-01 00:00:00' default",
        metavar="DATETIME")

    group.add_option("--start-rowid",
        action="store", dest="start_rowid", type=int, default=1,
        help="reset given worker's start rowid. 1 default",
        metavar="ROWID")

    group.add_option("--end-time",
        action="store", dest="end_time", type="string", default=None,
        help="specify the end time to stop workers. None (default)",
        metavar="DATETIME")

    group.add_option("--end-rowid",
        action="store", dest="end_rowid", type=int, default=None,
        help="specify the end rowid to stop workers. None (default)",
        metavar="ROWID")

    group.add_option("--startup",
        action="store_true", dest="startup", default=False,
        help="startup given worker logger")

    group.add_option("--batch-rows",
        action="store", dest="batch_rows", type=int, default=5000,
        help="specify batch rows for logger. 5000 default",
        metavar="ROWS")

    group.add_option("--force",
        action="store_true", dest="force", default=False,
        help="force apply on all workers")

    if len(sys.argv) == 1:
        elog.warn("WORKERs not specified")
        print "--------------------------------"
        parser.print_help()
        print "--------------------------------"
        exit(1)

    workers = None
    firstarg = sys.argv[1]
    if not firstarg.startswith('-'):
        workers = []
        names = firstarg.split(',')
        for name in names:
            workers.append(name.strip(' '))
        pass

    config = {
        'loggers' : workers,
        'logger' : {
            'logging_config': os.path.join(APPHOME, 'conf/logger.config'),
            'file': APPNAME + '.log',
            'name': 'main'
        },
        'loggers_abspath' : os.path.join(APPHOME, "loggers")
    }

    main(config, parser)

    sys.exit(0)
