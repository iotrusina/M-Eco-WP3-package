#!/usr/bin/env bash

export JAVA_HOME=/usr/local/share/Java64
. /mnt/minerva1/nlp/projects/spinn3r/pythoninit
ulimit -t unlimited 

cd /mnt/minerva1/nlp/projects/spinn3r/master
./master.py $1
