## galaxy_loggers

**本软件不提供任何保证。使用本软件造成的后果本人概不负责。**

All rights reserved.

A set of python scripts for producing a mass of test files (.csv).

一个多进程框架。每个进程 (loggers/weblogger.py) 生成测试日志文件。可以修改代码，使之用于其它目的。

- 必备(Prerequisites):

    	python2 + yaml

- Ubuntu18.04:

        $ sudo apt install python-minimal
        $ sudo apt install python-yaml

### 如何增加一个进程 (How to add a logger worker)


	$ bin/galaxy_loggers.py --add-logger


### 如何减少一个进程 (How to remove a logger worker)

	$ bin/galaxy_loggers.py --remove-logger

### 显示当前有哪些进程 (How to display all loggers)

	$ bin/galaxy_loggers.py --list


### 如何改变配置文件指定日志文件的最大字节数和文件数 (How to change the config for max size in bytes of each log file)

 - 改变 conf/logger.config 的内容如下 (change values in logger.config as below):

        maxBytes: 2147483647   2GB (default)
        backupCount: 2000      2000 files (default)


    $ vi conf/logger.config

	    weblogger_handler:
	        class: utils.cloghandler.ConcurrentRotatingFileHandler
	        level: NOTSET
	        maxBytes: 2147483647
	        backupCount: 2000
	        delay: true
	        filename: '/dev/null'
	        formatter: simple


### 启动进程 (Start loggers)


	$ sudo bin/ctlservice.sh debug

  or

    $ sudo bin/ctlservice.sh start


### 关闭全部进程 (Stop all loggers)


	$ sudo bin/ctlservice.sh stop

  or

    $ sudo bin/ctlservice.sh kill


生成的文件默认在 tmp/stash/ 下，也可以更改 (--stash=YOUR_STASH_DIR)。程序本身的日志在 applog/ 下， 如果 applog 目录不存在需要手工创建。

	logger files will be generated default in: tmp/stash/
	
	and you may change it by specify: --stash=YOUR_STASH_DIR
	
	see: galaxy_loggers.py: line 292 stash_dir = ...

