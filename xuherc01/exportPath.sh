#!/bin/sh

# Export promennych pro spravnou funkcnost rrs_local
# Funguje na serveru athena3

export NLP=/mnt/minerva1/nlp
#export PYTHONPATH=$PYTHONPATH:/mnt/minerva1/nlp/local/lib/python2.5/site-packages
#export PATH=$NLP/local/bin:$NLP/local/usr/bin:$PATH
export LD_LIBRARY_PATH=$NLP/local/lib:$LD_LIBRARY_PATH
export NLTK_DATA=$NLP/local/share/nltk_data
#export PYTHONPATH=$PYTHONPATH:/mnt/minerva1/nlp/projects/spinn3r/modules/
#export PATH=/mnt/minerva1/nlp/local/bin:$PATH
#export PATH=/mnt/minerva1/nlp/software/TreeTagger/cmd/:$PATH


export PATH="/mnt/data2/rrs_local/bin:/mnt/minerva1/nlp/software/TreeTagger/cmd:$PATH"
export LD_LIBRARY_PATH="/mnt/data2/rrs_local/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="/mnt/data2/rrs_local/lib/python2.7/"

