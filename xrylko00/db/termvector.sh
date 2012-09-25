#!/usr/bin/env bash

. /mnt/minerva1/nlp/projects/spinn3r/newpythoninit
ulimit -t unlimited 
cd /mnt/minerva1/nlp/projects/spinn3r/db/
./termvector.py >termvector.std.log 2>termvector.err.log
