#!/usr/bin/env bash

export JAVA_HOME=/usr/local/share/Java64
. /mnt/minerva1/nlp/projects/spinn3r/pythoninit
ulimit -t unlimited 
cd /mnt/minerva1/nlp/projects/meco/stanford_ner
DIR=/mnt/minerva1/nlp/projects/spinn3r/db
$DIR/affectedOrganism.py en > $DIR/affected.log 2>$DIR/affected.err.log
