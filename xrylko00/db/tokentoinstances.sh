#!/usr/bin/env bash

. /mnt/minerva1/nlp/projects/spinn3r/newpythoninit
ulimit -t unlimited 

DIR=/mnt/minerva1/nlp/projects/spinn3r/db
cd $DIR

./tokentoinstances.py en > ./tokentoinstances.log 2>./tokentoinstances.err.log
