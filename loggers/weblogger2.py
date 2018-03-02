#!/usr/bin/python
#-*- coding: UTF-8 -*-
#
# weblogger.py
#
#   生成测试数据文件
#
#   see: $APPHELP
#
# ZhangLiang, 350137278@qq.com
#
# LOGS:
#   -- 2017-12-08: first created
#   -- 2017-12-11: last updated
########################################################################
import os, sys, time, yaml, random, inspect

from time import strftime, localtime
from datetime import timedelta, date
import calendar

import logging, logging.config

import common
import utils.utility as util
import utils.evntlog as elog

########################################################################
# ! DO NOT CHANGE BELOW !
logger_module_name, _ = os.path.splitext(os.path.basename(inspect.getfile(inspect.currentframe())))

########################################################################
def create_logger_instance(config):
    return WebLogger(**config)


def timestamp2datetimestr(ts, dt_format):
    dt = time.localtime(ts)
    return time.strftime(dt_format, dt)


def datetimestr2timestamp(dtstr, dt_format):
    st_dt = time.strptime(dtstr, dt_format)
    return int(time.mktime(st_dt))


def log_messages(loggerClass):
    tstamp = loggerClass.start_tstamp
    rowid = loggerClass.start_rowid
    time_str = timestamp2datetimestr(tstamp, WebLogger.DATE_FORMAT)

    loggerClass.save_position((tstamp + WebLogger.TIME_DELTA, rowid + loggerClass.batch_rows))

    elog.debug("%s: save position (%d, %d)", loggerClass.getlogfilename(), loggerClass.start_tstamp, loggerClass.start_rowid)

    random.seed(loggerClass.start_tstamp)

    while rowid < loggerClass.start_rowid:
        loggerClass.log_message(rowid, tstamp, time_str)
        rowid = rowid + 1
        pass

    pass


class WebLogger(object):
    LOGGER_CATALOG = logger_module_name

    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    START_DTSTR = '2000-01-01 00:00:00'
    START_ROWID = 1

    TIME_DELTA = 1

    def __init__(self, **kwargs):
        self.logger_name = WebLogger.LOGGER_CATALOG

        self.batch_rows = kwargs['batch_rows']
        self.dictcfg = kwargs['logger_config']

        self.log_prefix = kwargs['logger_stash']

        self.plugins_dir = common.script_abspath()
        self.position_file = os.path.join(self.plugins_dir, ".%s.position" % self.logger_name)

        filename_format = "%s_%s.csv" % (self.logger_name, time.strftime("%Y%m%d%H"))

        self.init_data(os.path.join(self.log_prefix, filename_format))
        pass


    def __del__(self):
        self.cleanup()
        pass


    def cleanup(self):
        removehandlers = []
        for handler in self.logger.handlers:
            removehandlers.append(handler)

        for handler in removehandlers:
            if handler.stream:
                elog.debug("close stream: %r", self.logfile)
                handler.stream.close()
            try:
                self.logger.removeHandler(handler)
            except TypeError as err:
                pass
        pass


    def save_position(self, position = None):
        if position:
            (self.start_tstamp, self.start_rowid) = position

        line = "%d,%d\n" % (self.start_tstamp, self.start_rowid)
        util.write_first_line_nothrow(self.position_file, line)
        pass


    def restore_position(self):
        is_dirty, start_tstamp, start_rowid = (False, 0, 0)

        if util.file_exists(self.position_file):
            line = util.read_first_line_nothrow(self.position_file)
            t = line.split(',')
            if len(t) == 2:
                (start_tstamp, start_rowid) = (int(t[0]), int(t[1]))
            pass

        if start_tstamp == 0:
            start_tstamp = datetimestr2timestamp(WebLogger.START_DTSTR, WebLogger.DATE_FORMAT)
            is_dirty = True

        if start_rowid == 0:
            start_rowid = WebLogger.START_ROWID
            is_dirty = True

        self.start_tstamp = start_tstamp
        self.start_rowid = start_rowid

        if is_dirty:
            self.save_position()
        pass


    def init_data(self, logfile):
        self.restore_position()

        if not util.dir_exists(self.log_prefix):
            elog.warn("create dir for stash log: %s", self.log_prefix)
            os.makedirs(self.log_prefix)

        elog.debug('log config: %r', self.dictcfg)
        elog.info('stash prefix: %s', self.log_prefix)
        elog.info('start tstamp: %d', self.start_tstamp)
        elog.info('start rowid: %d', self.start_rowid)
        elog.info('batch rows: %d', self.batch_rows)

        file_dests = os.path.join(self.plugins_dir, 'config' , 'dests.csv')
        file_proxys = os.path.join(self.plugins_dir, 'config' , 'proxys.csv')
        file_keywds = os.path.join(self.plugins_dir, 'config' , 'keywds.csv')

        elog.info("dests file: %s", file_dests)
        elog.info("proxys file: %s", file_proxys)
        elog.info("keywds file: %s", file_keywds)

        with open(file_dests) as fd:
            dests = fd.readlines()

        with open(file_proxys) as fd:
            proxys = fd.readlines()

        with open(file_keywds) as fd:
            keywds = fd.readlines()

        self.dests = []
        for n in range(0, len(dests)):
            # id, ip, port, host
            # 100005,67.64.46.91,80,www.zhibo8.cc
            self.dests.append(tuple(dests[n].strip('\n').split(',')))
        del dests

        self.proxys = []
        for n in range(0, len(proxys)):
            # ip, port, type
            # 121.232.144.158,9000,HTTP
            self.proxys.append(tuple(proxys[n].strip('\n').split(',')))
        del proxys

        self.keywds = []
        for n in range(0, len(keywds)):
            # id, word
            self.keywds.append(tuple(keywds[n].strip('\n').split(',')))
        del keywds

        self.max_dests = len(self.dests) - 1
        self.max_proxys = len(self.proxys) - 1
        self.max_keywds = len(self.keywds) - 1

        # update dictcfg with logfile
        elog.update_log_config(self.dictcfg, self.logger_name, logfile, 'INFO')

        # reload config
        logging.config.dictConfig(self.dictcfg)

        # update logger
        self.logger = logging.getLogger(self.logger_name)
        self.logfile = logfile

        (self.a, self.b, self.c, self.d, self.p) = ((1, 220), (10, 230), (20, 240), (30, 250), (10000, 60000))

        self.fields = (
            'rowid',
            'timestr',
            'timeint',
            'destid',
            'sourip',
            'sourport',
            'destip',
            'destport',
            'desturl',
            'proxyip',
            'proxyport',
            'proxytype',
            'keywdid')
        pass


    def setlogfile(self, logfile):
        if self.logfile != logfile:
            ###elog.debug("using: %r", logfile)
            self.cleanup()
            self.init(logfile)


    def getlogfilename(self):
        return os.path.basename(self.logfile)


    def log_message(self, rowid, tstamp, time_str):
        (a1, a2) = self.a
        (b1, b2) = self.b
        (c1, c2) = self.c
        (d1, d2) = self.d
        (p1, p2) = self.p

        a = random.randint(a1, a2)
        b = random.randint(b1, b2)
        c = random.randint(c1, c2)
        d = random.randint(d1, d2)

        sourip = "%d.%d.%d.%d" % (a, b, c, d)
        sourport = random.randint(p1, p2)

        i = random.randint(0, self.max_dests)
        j = random.randint(0, self.max_proxys)
        k = random.randint(0, self.max_keywds)

        # id, ip, port, host
        dest = self.dests[i]

        # ip, port, type
        proxy = self.proxys[j]

        # id, word
        keywd = self.keywds[k]

        # rowid,timestr,timeint,destid,sourip,sourport,destip,destport,desturl,proxyip,proxyport,proxytype,keywdid
        # 12345,2012-12-22 12:23:56,167123456,133455,123.31.171.72,58084,141.86.84.100,80,jumpinyougame.com,113.58.235.107,3128,HTTP,117
        message = "%d,%s,%d,%s,%s,%d,%s,%s,%s,%s,%s,%s,%s" % \
            (rowid, time_str, tstamp, dest[0], sourip, sourport, dest[1], dest[2], dest[3], proxy[0], proxy[1], proxy[2], keywd[0])

        # use critical to ensure alway output message
        self.logger.critical(message)
        pass
