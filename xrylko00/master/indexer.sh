#!/usr/bin/env bash

. /mnt/minerva1/nlp/projects/spinn3r/pythoninit
ulimit -t unlimited 

PYTHONPATH=$PYTHONPATH:/mnt/minerva1/nlp/projects/spinn3r/db
cd /mnt/minerva1/nlp/projects/spinn3r/master
./db_indexer.sh 2>indexer.err.log >indexer.log
