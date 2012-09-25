#!/usr/bin/env python
import sys
sys.path.append("/mnt/minerva1/nlp/projects/meco/stanford_ner")
from extract_victims import *
from autoapi.autoapi import *
import re
import timer
import psycopg2

ENTTYPE_ID = 62 # AffectedOrganism
MAX_LEN    = 255 # max length of `exact` (and entity, ...)

"""
Adds entities for documents.

Take one argument - language (en, de, ...)
"""

prog = re.compile( ".*[a-z].*", re.I )
def is_entity_ok( entity ):
    return prog.match( entity ) is not None
    

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    (Split list into small `n-size` lists.)
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def affect_docs( documents, language, cursor ):
    """
    Get documents, join texts, extract_victims and add properly instances.
    All documents have to have same language
    """
    print "DOCUMENTS COUNT =", len( documents ) 
    offset = 0
    jointext = list()
    boundaries = dict()
    for doc in documents:
        text = doc.get_text()
        id = doc.get_id()
        length = len( text )
        boundaries[id] = (offset, length)
        jointext.append( text )
        offset += length + 1 # 1 for \n in join
    text = "\n".join( jointext )    
    instances = extract_victims( text, language )
    print "======================="
    print instances
    if len(instances) == 0:
        print "INSTANCES - None"
    else:
        for instance in instances:
            offset, length, exact = instance
            exact = unicode(exact, 'utf-8')
            if not is_entity_ok( exact ):
                print "IGNORING", repr(exact)
                continue
            if len( exact ) >= MAX_LEN:
                continue
            #entity = Entities(name=exact, enttype_id=ENTTYPE_ID,
            #        normalized_entity=exact.lower().strip().lstrip('#'))
            cursor.execute("""select * from insert_entity(%s, %s)""",
                    (exact, ENTTYPE_ID))
            entity_id = cursor.fetchone()[0]
            try:
                assert entity_id != None
                # determine document id
                doc_id = None
                for id, (b_offset, b_length) in boundaries.iteritems():
                    if offset >= b_offset and offset < ( b_offset + b_length ):
                        # starts in text, should also end in text:
                        if ( offset + length ) <= ( b_offset + b_length ):
                            # OK!
                            print id
                            #print "Offset", offset, "length", length, "b_offset", b_offset, "b_length", b_length
                            doc_id = id
                            break
                        else:
                            if "\n" in exact:
                                # entity is for sure over 2 items
                                doc_id = None
                                break
                            print "ID=", id
                            print "EXACT=", exact
                            print "OFFSET=", offset-b_offset + 1
                            print "LENGTH=", length
                            raise Exception("Weird entity! entity=%s" % exact)
                if ( doc_id is None ):
                    # skip
                    continue
                print "EXACT=", repr(exact)
                print "OFFSET=", offset-b_offset + 1
                print "LENGTH=", length
                assert ( ( offset - b_offset ) >= 0 )
                assert ( length > 0 )
                assert ( doc_id > 0 )
                assert ( len( exact ) > 0 )
                inst_db = Instances(entity_id=entity_id,
                        item_id = doc_id,
                        exact = exact,
                        length = length,
                        offset_ = offset - b_offset) # correction of offset
                try:
                    inserted, id = inst_db.insert()
                except psycopg2.IntegrityError, e:
                    print "EXCEPTION", e
                else:
                    print "INSTANCE", id, " DOCUMENT", doc_id
            #except AttributeException, e:
            except NotImplementedError, e:
                print "EXCEPTION", e
    # OK!
    for doc in documents:
        doc.set__affected( True )
        doc.update()

def test():
    language = sys.argv[1]
    CHUNK_SIZE = 10
    cursor = Documents.conn.cursor()
    while True:
        documents = MDocuments()
        LIMIT = CHUNK_SIZE * 5
        documents.get_multi(limit = LIMIT,
                where="""id IN (SELECT id FROM documents_to_affected 
                                WHERE language='%s' LIMIT %d)""" % (language, LIMIT))
        docs = [Documents(**d) for d in documents.value()]
        if len(docs) == 0:
            print "NO DOCUMENTS!\nSLEEPING."
            timer.sleep_minute( 120 )
            continue
        c = 0
        for documents in chunks( docs, CHUNK_SIZE ):
            affect_docs( documents, language, cursor )

if __name__ == '__main__':
    test()
