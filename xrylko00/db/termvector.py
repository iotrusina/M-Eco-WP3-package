#!/usr/bin/env python2.7

import sys
reload(sys)
sys.setdefaultencoding("utf8")
from autoapi.connection import get_connection
import timer
import psycopg2
import nltk

tokenizer = dict()
tokenizer['de'] = nltk.data.load('tokenizers/punkt/dutch.pickle')
tokenizer['en'] = nltk.data.load('tokenizers/punkt/english.pickle')
tokenizer['fr'] = nltk.data.load('tokenizers/punkt/french.pickle')

supported_langs = tokenizer.keys()

def get_termvector(text, lang, conn):
    if lang not in supported_langs:
        return None
    cursor = conn.cursor()
    sentence_num = -1
    occ = dict()
    for sentence in tokenizer[lang].tokenize(text):
        sentence_num += 1
        tokens = nltk.word_tokenize(sentence)
        # get for each token id from database
        for token in tokens:
            cursor.execute('select * from inserting_terms_f(%s);', ( token,))
            id = cursor.fetchone()
            id = id[0]
            # create occurence count:
            if id in occ:
                occ[id] = occ[id] + 1 
            else:
                occ[id] = 1
    pairs = []
    for id, counts in occ.iteritems():
        pairs.append( (id, counts) )
    # sort and make string
    restokens = []
    for id, occ_token in sorted(pairs, key = lambda a : a[0] ):
        restokens.append( '%s:%d' % (id, occ_token) )
    termvector = ' '.join( restokens )
    return termvector


if __name__ == "__main__":
    LIMIT = 20
    conn = get_connection(UNICODE=True)
    #conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    print "Analyzing whole database"
    sys.stdout.flush()
    while True:
        curr = conn.cursor()
        curr.execute("""SELECT id, language, text FROM documents WHERE termvector is null and language in ('en', 'de') 
                and pubdate>='01-05-2011' and pubdate<'01-07-2011' 
                LIMIT %s""", (LIMIT ,))
        #curr.execute("""SELECT id, text FROM documents WHERE id=20875243""")
        count = 0
        for document in curr:
            id, lang, text = document
            print "id=%s" % id
            termvector = get_termvector(text, lang, conn)
            insertcurr = conn.cursor()
            insertcurr.execute("""UPDATE documents
                    SET termvector=%s
                    WHERE id=%s""", ( termvector, id ))
            count += 1
            sys.stdout.flush()
        if count == 0:
            print "SLEEPING"
            timer.sleep_minute(60)
        



