# galaxy_loggers
A set of python scripts for producing a mass of test files (.csv).

生成海量测试日志文件的 python 脚本。

## How to add a logger worker

 - Copy a logger from existing one (NN is a number)

```
    $ cd ${galaxy_loggers}/loggers/
    $ cp weblogger.py webloggerNN.py
```

 - Add a logger handler under loggers section in logger.config

```
    $ cd ${galaxy_loggers}/conf/
    $ vi logger.config

...

loggers:
    ...

    webloggerNN:
        level: NOTSET
        handlers: [weblogger_handler]
        propagate: no

...

```

## How to change the config for max size in bytes of each log file

 - change values in logger.config as below:

        maxBytes: 2147483647   2GB (default)
        backupCount: 2000      2000 files (default)


```
    $ cd ${galaxy_loggers}/conf/
    $ vi logger.config

    weblogger_handler:
        class: utils.cloghandler.ConcurrentRotatingFileHandler
        level: NOTSET
        maxBytes: 2147483647
        backupCount: 2000
        delay: true
        filename: '/dev/null'
        formatter: simple
```

## Start loggers


```
    $ cd ${galaxy_loggers}/bin/

    $ sudo ./bin/loggers.sh start

  or:

    $ ./bin/loggers.sh start

```

logger files will be generated default in: ${galaxy_loggers}/tmp/stash/

and you may change it by specify: --stash=YOUR_STASH_DIR

see: ctls_galaxy_loggers.py: line 292 stash_dir = ...
