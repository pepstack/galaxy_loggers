#!/usr/bin/python
#-*- coding: UTF-8 -*-
#
# phoenixdb_test.py
#
#   测试 phoenixdb
#
#   see: $APPHELP
#
# ZhangLiang, 350137278@qq.com
#
# @create: 2018-07-12
# @update:
#
########################################################################
import os, sys, time, yaml, random, inspect

from time import strftime, localtime
from datetime import timedelta, date
import calendar

import phoenixdb, phoenixdb.cursor

import logging, logging.config

import common
import utils.utility as util
import utils.evntlog as elog

########################################################################
# ! DO NOT CHANGE BELOW !
logger_module_name, _ = os.path.splitext(os.path.basename(inspect.getfile(inspect.currentframe())))

########################################################################

class PhoenixdbTest(object):

    def __init__(self, **kwargs):
        # http://localhost:8765/
        self.dburl = kwargs['dburl']
        
        # autocommit = True
        self.autocommit = kwargs['autocommit']

        self.conn = phoenixdb.connect(self.dburl, autocommit = self.autocommit)
        pass


    def __del__(self):
        self.cleanup()
        pass


    def cleanup(self):
        if self.conn:
            self.conn.close()
        pass


    def getCursor(self):
        cursor = self.conn.cursor()
        return cursor
