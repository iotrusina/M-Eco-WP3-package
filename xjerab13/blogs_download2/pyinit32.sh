ulimit -t unlimited
export NLP=/mnt/minerva1/nlp
export PYTHONPATH=/mnt/minerva1/nlp/local/lib/python2.5/site-packages
export PATH=$NLP/local/bin:$NLP/local/usr/bin:$PATH
export LD_LIBRARY_PATH=$NLP/local/lib:$LD_LIBRARY_PATH
export NLTK_DATA=$NLP/local/share/nltk_data