#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from autoapi.connection import get_connection
import timer

from nltk.tokenize import sent_tokenize
from nltk.tokenize import TreebankWordTokenizer, WhitespaceTokenizer, PunktSentenceTokenizer

class Tokenizer(TreebankWordTokenizer):
    def _slices_from_text(): 
        yield slice(last_break, match.end()) 
    #def _sentences_from_text(self, text): 
    #    return (text[sl] for sl in self._slices_from_text(text))

    def span_tokenize(self, text):
        return [ sl for sl in self._slices_from_text(text) ]

    def _slices_from_text(self, text):
        for m in self.REGEX.finditer(text):
            subgroups = m.groups()
            for i in range(1, m.lastindex+1):
                span = m.span(i)
                if span[0] < 0:continue
                s = subgroups[i-1]
                if s.strip() == "": continue
                yield span

def main():
    conn = get_connection(UNICODE=True)
    curr = conn.cursor()
    tokenizer = TreebankWordTokenizer()

    while True:
        curr.execute("""SELECT id, text, language FROM documents 
                WHERE
                --guid='tw:122144569302323201'
                EXISTS ( SELECT 1 FROM instances WHERE item_id=documents.id AND begintoken IS NULL)
                LIMIT 1""")
        data = curr.fetchone()
        if data is None:
            print "sleep"
            timer.sleep_minute(30)
            continue
        id, text, lang = data
        print "id", id
        curr.execute("""SELECT * FROM instances
                WHERE item_id = %s
                AND begintoken IS NULL""", (id,))
        # throw away `confidence`
        instances = [list(x)[:-1] for x in curr]
        if not len(instances):
            continue
        instance_ = []
        for ins in instances:
            ins[-1] = None
            ins[-2] = None
            ins[-3] = None
            instance_.append(ins)
        instances = instance_
        #print instances

        sent_tok = PunktSentenceTokenizer()

        for sid, sentidx in enumerate(sent_tok.span_tokenize(text)):
            #print '++++'
            sentence = text[sentidx[0]:sentidx[1]]
            #print sentence
            #print '----'
            for pos, indexes in enumerate(WhitespaceTokenizer().span_tokenize(sentence)):
                # TODO indexy jsou pouze relativni k vete
                # ale instances je ma od zacatku!
                indexes = list(indexes)
                indexes[0] = sentidx[0] + indexes[0]
                indexes[1] = sentidx[0] + indexes[1]
                word = text[indexes[0]:indexes[1]]
                #print pos, word, indexes

                for i, instance in enumerate(instances):
                    id, entity_id, item_id, exact, offset, length, sid_, begin, end  =instance
                    #print i,instance
                    if sid_ is None:
                        if begin is None:
                            if offset >= indexes[0] and offset <= indexes[1]:
                                instances[i][-2] = begin = pos
                                instances[i][-3] = sid_ = sid
                    if sid_ == sid:
                        if end is None and begin is not None:
                            off = offset + length
                            if off <= indexes[1] and off >= indexes[0]:
                                instances[i][-1] = pos
                                if off == indexes[0]:
                                    instances[i][-1] = pos - 1
        for instance in instances:
            print instance
            id, entity_id, item_id, exact, offset, length, sid, begin, end =instance
            #print exact, ">>", sid, begin, end
            if end is None:
                if not " " in exact:
                    end = begin
                else:
                    end = -1
            curr.execute("""UPDATE instances
                    SET sid=%s, begintoken=%s, endtoken=%s
                    WHERE id=%s""", (sid, begin, end, id))
if __name__ == '__main__':
    main()
