#!/usr/bin/env python2.7

import timer
import sys
import os
from datetime import date
import psycopg2
import csv
import codecs
import cStringIO
from autoapi.connection import get_connection


FOLDER = '/homes/eva/xr/xrylko00/spinn/spinn3r/master/DATA/'

# statistical
fileTotal     = open(FOLDER+'total.dat', 'a')
fileAnalyzed  = open(FOLDER+'analyzed.dat', 'a')
fileDiseases  = csv.writer(open(FOLDER+'diseases.txt', 'w'), delimiter="\t")



class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)





# data output
fileDataDiseases = UnicodeWriter(open(FOLDER+'diseases_list.dat', 'w'),
                                 dialect = csv.excel)
fileDataSymptoms = UnicodeWriter(open(FOLDER+'symptoms_list.dat', 'w'),
                                dialect = csv.excel)

conn = get_connection(UNICODE=True)
cur = conn.cursor()
today = '%s' % date.today()


## count douments by languages
#cur.execute("""select language, count(*) from documents group by language""")
#for lang, count in cur:
#    f = open(FOLDER + 'languages-%s.dat' % lang, 'a')
#    f.write("%s\t%d\n" % ( today, count ))
#    f.flush()
#    f.close()
#cur.execute("""select count(*) from documents where language not in ('en', 'de')""")
#(count,) = cur.fetchone()
#f = open(FOLDER + 'languages-others.dat', 'a')
#f.write("%s\t%s\n" % (today, count))
#f.flush()
#f.close()
#
#
## detailed analyzed out
#langs = ['de', 'en']
#for lang in langs:
#    cur.execute("""select count(*) from documents where language=%s and _stanford=%s""", (lang, True))
#    fileAnalyzedDet = open(FOLDER+'analyzed_det_%s.dat'%lang, 'a')
#    fileAnalyzedDet.write('%s\t%d\n' % (today, cur.fetchone()[0]) )
#    fileAnalyzedDet.close()
#
#
#
## Affected 
#fileAffected = open(FOLDER+'affected.dat', 'a')
#cur.execute('SELECT COUNT(1) FROM documents WHERE _affected=%s', (True, ))
#affected = cur.fetchone()[0]
#
#fileAffected.write('%s\t%s\n' % (today, affected))
#fileAffected.close()
#
## COUNT
#cur.execute('SELECT COUNT(1) FROM documents;')
#total = cur.fetchone()[0]
#fileTotal.write('%s\t%s\n' % (today, total))
#fileTotal.close()
#
## ANALYZE
#cur.execute('SELECT COUNT(1) FROM documents where _analyzed=True;')
#total = cur.fetchone()[0]
#fileAnalyzed.write('%s\t%s\n' % (today, total))
#fileAnalyzed.close()
#
#cur.execute('select language, count(1) from diseases group by language') 
#fileDiseases.writerows(cur)
## it's not file! fileDiseases.close()
#
## SOURCES
#cur.execute("""select count(*) as documents_count, lower(section) from documents, sources
#where sources.id=documents.source_id group by lower(section)
#order by lower(section);""");
#for row in cur:
#    count, section = row
#    sfile = open(FOLDER+'source-'+section+'.txt', 'a')
#    sfile.write('%s\t%s\n' % (today, count))
#    sfile.close()

# dieseas data output
cols = ['disease', 'language']
cur.execute('select %s from diseases' % ", ".join(cols))
fileDataDiseases.writerow(cols)
for row in cur:
    fileDataDiseases.writerow(row)

# symptoms data out
cols = ['symptom', 'language']
cur.execute('select %s from symptoms' % ", ".join(cols))
fileDataSymptoms.writerow(cols)
for row in cur:
    fileDataSymptoms.writerow(row)








