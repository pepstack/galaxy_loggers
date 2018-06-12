# galaxy_loggers
A set of python scripts for producing a mass of test files (.csv).

Prerequisites:

    python2 + yaml

On ubuntu1804:

   $ sudo apt install python-minimal
   $ sudo apt install python-yaml


生成海量测试日志文件的 python 脚本。

## How to add a logger worker

```
    $ ${galaxy_loggers}/ctls_galaxy_loggers.py --add-logger
```

## How to remove a logger worker

```
    $ ${galaxy_loggers}/ctls_galaxy_loggers.py --remove-logger
```

## How to list all logger workers

```
    $ ${galaxy_loggers}/ctls_galaxy_loggers.py --list
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
