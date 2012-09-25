#!/usr/bin/env bash

export JAVA_HOME=/usr/local/share/Java64
. /mnt/minerva1/nlp/projects/spinn3r/newpythoninit
ulimit -t unlimited 

cd /mnt/minerva1/nlp/projects/spinn3r/master
./crontab.sh > crontab.log 2>crontab.err.log
#python ./cron.py > cron.log 2>cron.err.log
