#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, traceback
reload(sys)
sys.setdefaultencoding('utf-8')
from lxml import etree
from StringIO import StringIO

from autoapi.connection import get_connection
from autoapi.autoapi import MInstances, Instances

OKDOC=0

MAPPER = {
'('  : ['['], 
')'  : [']'],
'``' : ['"', u'«', u'“'],
"''" : ['"', u'»'],
"'"  : ["`"],
'`'  : ["'"]}

def epositionPlain(tokens, plain):
    """ produce token positions coming from a plain text
    yield (token, startoffset, endoffset, tokenposition, sid)

    @token (token, tokenposition, sid)
    """
    # simulate
    #print "\n\n\nEPOSITION"

    #print plain.encode('utf-8')
    #plain = plain.decode('utf-8')
    p = 0
    for tok in tokens:
        token, tokenposition, sid = tok
        t = token

        #st = MAPPER.get(t, t)
        i = plain.find( t.encode('utf-8') )
        if t == '?' and i > 10:
            # something wrong, probably '?' means bad character (encoding)
            # and not real '?'
            # so try again
            i = -1
        if i == -1:
            if t == '?':
                # unknown characer (bad encoding)
                # so get nearest non-white character as "matching"
                stripped = plain.lstrip(' ')
                i = len( plain ) - len( stripped ) 
                t = stripped[0]
                #print repr(t)
                #print repr(plain[0:20])
                #print "? taken as", t, "in ", plain[0:20]
            else:
                # so try mapping:
                st = MAPPER.get(t, [t])
                print "Mapping %s -> %s" % (t.encode('utf-8'), st)
                match = False
                for sst in st:
                    if sst == t:
                        # try something else
                        sst = t
                        sst = sst.replace("\/", "/")
                        sst = sst.replace("\*", "*")
                    i = plain.find(sst.encode('utf-8'))
                    if i != -1:
                        t = sst
                        match = True
                        break
                if match: assert i != -1
                if match:
                    if i > 5:
                        # it is weird to has i > 10 when mapping 
                        # (should be next char...)
                        i = -1
        
        if i == -1:
            print "ERROR"
            print "TOKEN", t.encode('utf-8')
            print "TOKEN", repr(t)
            #print "TEXT", plain.encode('utf-8')
            print "TEXT", repr(plain)
            raise IndexError("Can not find TOKEN in TEXT. OKDOCS=%d" % OKDOC)
        
        l = len(t)
        #print "\n\n", "="*30
        #print token, " : ", plain
        plain = plain[i + l : len(plain)]
        #print " "*len(token), " : ", plain

        yield (token, p + i, p + i + l, tokenposition, sid)

        p += i + l


def iter_entities(instances):
    for instance in instances:
        yield (int(instance.get_offset_()), 
                int(instance.get_offset_())+int(instance.get_length()), 
                instance)

def edit_instances(instances, tokens):
    # text in unicode

    #text = text #.encode("latin1", "replace")

    # hack to allow `` and '' sequences to appear
    #text = text.replace("``", " \"")
    #text = text.replace("''", "\" ")
    #text = text.replace("`", "'")
    
    entities = [x for x in iter_entities(instances)]
    entities.sort(key=lambda x:x[0])

    annots = iter(entities)

    def getnext(i):
        try:
            return i.next()
        except StopIteration:
            return None

    
    open = []
    a = getnext(annots)

    for (form, begin, end, index, sid) in tokens:
        #debug(str(form), str(index), str(begin), str(end))

        while a != None and a[0] < end:
            if a[1] >= begin:
                #debug("####", a[0], a[1], index)
                open.append ( (a, (sid, index) ) )
            a = getnext(annots)

        closing = []
        newopen = []
        for oa in open:
            if oa[0][1] <= end:
                #debug("%%%%", oa[0][0], oa[0][1], index)
                closing.append (oa)
            else:
                newopen.append (oa)
        open = newopen

        deleted = []
        for (begin, end, instance), (si, i) in closing:
            if instance in deleted:
                print "ALREADY IN DELETED!"
                continue
            if not si == sid:
                print "SI != SID\tsi=", si, "sid=",sid
                #instance.remove_by_id()
                deleted.append( instance )
                continue
            instance.set_begintoken(i)
            instance.set_endtoken(index)
            instance.set_sid(si)
            instance.update()
            #print "\n\n\n", instance.toxml()
            print "<<< begintoken = ", i
            print "<<< endtoken = ", index
            print "<<< sid = ", si



def iter_tokens(sentences):
    """
    yield (token, tokenposition, sid)
    """
    sentswithroot = "<root>%s</root>" % sentences
    root = etree.fromstring( sentswithroot )
    for sentence in root:
        sid = int(sentence.get('id'))
        tokens = sentence.xpath('./tokens/text()')[0]
        pos = 0
        for token in tokens.split(" "):
            if len(token.strip()) == 0:
                continue
            yield (token, pos, sid)
            pos += 1
        

def get_tokens(txt, sentences):
    tokens = [token  for token in iter_tokens(sentences)]
    return [_ for _ in epositionPlain(tokens, txt)]

    

def analyze(id, txt, sentences):
    print ">>> Documemnt ID = %s" % id
    errmsg = None
    if not len(txt):
        return "empty text"
    tokens = get_tokens(txt, sentences)   

    minstances = MInstances()
    minstances.get_multi(where="""item_id=%d AND sid IS NULL
            AND 9!=(SELECT enttype_id FROM entities WHERE entities.id=entity_id)""" % id)
    #minstances.get_multi(where='item_id=%d' % id)
    instances = []
    for minst in minstances.value():
        instances.append(Instances(**minst))
    for i in instances : print ">>> Instance ID =", i.get_id()
    edit_instances(instances, tokens)
    return errmsg


def main():
    OKDOC = 0
    conn = get_connection()
    curr = conn.cursor()
    while True:
        curr.execute("""
                SELECT id, text, sentences FROM documents 
                WHERE language in ('de', 'en')
                -- and id = 18811 -- XXX
                --AND _stanford = True
                AND sentences IS NOT NULL
                AND EXISTS (
                    SELECT 1 FROM instances
                    WHERE 
                        item_id=documents.id 
                        AND sid IS NULL
                    )
                --ORDER BY random()
                LIMIT 50""")
        count = 0
        for doc in curr:
            id, text, sents = doc
            try:
                errmsg=analyze(id, text, sents)
                if errmsg:
                    print "ERROR", errmsg
                else:
                    OKDOC += 1
            except IndexError, e:
                print "Error for id = ", id
                print "IndexError", str(e)
            count += 1
        if count == 0:
            print "FINISH"
            break


if __name__ == "__main__":
    main()



