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

    
###

CREATE TABLE IF NOT EXISTS WEB_STAT (
     HOST CHAR(2) NOT NULL,
     DOMAIN VARCHAR NOT NULL,
     FEATURE VARCHAR NOT NULL,
     DATE DATE NOT NULL,
     USAGE.CORE BIGINT,
     USAGE.DB BIGINT,
     STATS.ACTIVE_VISITOR INTEGER
     CONSTRAINT PK PRIMARY KEY (HOST, DOMAIN, FEATURE, DATE)
);

1364991,2000-01-01 00:04:32,946656272,104810,123.152.206.146,58301,87.117.117.106,80,azly.cc,223.241.79.86,8010,HTTP,879
1364992,2000-01-01 00:04:32,946656272,113195,217.180.32.130,13437,211.52.78.212,80,corkiconscom,0.0.0.0,80,NUL,198
1364993,2000-01-01 00:04:32,946656272,164061,9.60.177.36,14225,42.92.238.28,80,thepinkonine.com,0.0.0.0,80,NUL,771
1364994,2000-01-01 00:04:32,946656272,144226,140.86.59.224,14984,93.208.113.21,8888,naijarushcom,0.0.0.0,80,NUL,597
1364995,2000-01-01 00:04:32,946656272,124815,177.79.170.45,38017,108.115.69.106,80,gogomatri.com,0.0.0.0,80,NUL,85
1364996,2000-01-01 00:04:32,946656272,143249,159.15.86.162,17549,201.87.204.68,80,multilevesystemwork.net,0.0.0.0,80,NUL,135
1364997,2000-01-01 00:04:32,946656272,154167,108.82.105.227,45959,166.142.185.75,8080,rollercoaterselfie.com,221.192.134.92,8081,HTTP,688
1364998,2000-01-01 00:04:32,946656272,134118,35.186.70.56,38697,160.142.96.37,80,katmaibeagirl.com,0.0.0.0,80,NUL,61
1364999,2000-01-01 00:04:32,946656272,142597,134.200.192.177,14099,90.81.193.38,80,moneyonthmind.com,0.0.0.0,80,NUL,418
1365000,2000-01-01 00:04:32,946656272,154530,42.94.172.181,38550,74.207.80.127,80,rubyonrais.cc,0.0.0.0,80,NUL,805

./sqlline.py ha06.ztgame.com,ha07.ztgame.com,ha08.ztgame.com:2181

CREATE TABLE IF NOT EXISTS "weblogger.csv" (
    "rowid" BIGINT NOT NULL,
    "timestr" DATE,
    "timeint" BIGINT,
    "dest.id" BIGINT,
    "sour.ip" VARCHAR(30),
    "sour.port" VARCHAR(10),
    "dest.ip" VARCHAR(30),
    "dest.port" VARCHAR(10),
    "dest.url" VARCHAR(255),
    "proxy.ip" VARCHAR(30),
    "proxy.port" VARCHAR(10),
    "proxy.type" VARCHAR(10),
    "keywdid" BIGINT,
    CONSTRAINT PK PRIMARY KEY ("rowid")
);

create index weblogger.ipaddr on weblogger(sour.ip,dest.ip)

CREATE INDEX async_index ON my_schema.my_table (v) ASYNC

hbase-site.xml:

<property>
  <name>hbase.regionserver.wal.codec</name>
  <value>org.apache.hadoop.hbase.regionserver.wal.IndexedWALEditCodec</value>
</property>

