ulimit -t unlimited
export NLP=/mnt/minerva1/nlp
export PYTHONPATH=/mnt/minerva1/nlp/local64/lib/python2.5/site-packages
export PATH=$NLP/local64/bin:$NLP/local64/usr/bin:$PATH
export LD_LIBRARY_PATH=/lib64:/usr/lib64:$NLP/local64/lib:$LD_LIBRARY_PATH
export NLTK_DATA=$NLP/local64/share/nltk_data