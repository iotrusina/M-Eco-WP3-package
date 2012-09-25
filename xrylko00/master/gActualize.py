#!/usr/bin/env python
# encoding: utf-8
import urllib2
import csv, codecs, cStringIO

import psycopg2
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
from autoapi.connection import get_connection
import timer

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

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

diseases_url = u'https://docs.google.com/spreadsheet/pub?hl=en_US&hl=en_US&key=0Amp0eSk0FNZSdGFPQlgtajlOdURXT1pfUTVkekFrZnc&single=true&gid=0&output=csv'
symptoms_url = u'https://docs.google.com/spreadsheet/pub?hl=en_US&hl=en_US&key=0Amp0eSk0FNZSdGFPQlgtajlOdURXT1pfUTVkekFrZnc&single=true&gid=1&output=csv'


# key : (url, [columns in db])
config = {'diseases' : (diseases_url, ['disease', 'language']),
          'symptoms' : (symptoms_url, ['symptom', 'language'])}

OUT_FOLDER = '/mnt/minerva1/nlp/projects/spinn3r/solr_data/fromdb/change/'
LOG_FILE   = '/mnt/minerva1/nlp/projects/meco/mg4j/server/root/xrylko00/logs/diseases_symptoms.txt'

def load(url):
    data = filter(
            lambda x: len(x) == 2 and all(x),
            (row for row in UnicodeReader(urllib2.urlopen(url))))
    data = [tuple(map(lambda y: y.lower(), x)) for x in data]
    data = set(data)
    # tuples to lists
    data = map(list, data)
    return data

if __name__ == '__main__':
    data = {}
    print "DATA FETCHING"
    for name, v in config.iteritems():
        url = v[0]
        data[name] = load(url)
        print "\t%s : %d" % (name, len(data[name]))

    print
    print "DB INTERACT"
    conn = get_connection()

    logfile = open( LOG_FILE, 'a')
    logfile.write("="*80)
    logfile.write("\nSTART (" + str(timer.timestamp()) + ')\n')
    outfile = open( OUT_FOLDER + str(timer.timestamp()) + '.csv', 'wb')
    csv_writer = UnicodeWriter(outfile)
    results = {}
    for name, values in data.iteritems():
        cols = config[name][1]
        cur = conn.cursor()
        cur.execute('select %s from %s' % (', '.join(cols), name))
        in_db = cur.fetchall()

        cur_insert = conn.cursor()
        print "\ttable : %s" % name
        print "\t\titems in db : %d" % (len(in_db))
        results[name] = 0
        for value in values:
            if tuple(value) not in in_db:
                print "\t\tnot in db : %s" % str(value)
                cur.execute('INSERT INTO %s (%s) VALUES (%%s, %%s) RETURNING id' % (name, ', '.join(cols)), value)
                id = cur.fetchone()
                logfile.write('\t"' + cur.query + '" = %d\n' % id[0])
                csv_writer.writerow([name] + value)
                results[name] += 1
    logfile.write("\nINSERTED\n")
    for k, v in results.iteritems():
        logfile.write("\t%s : %d\n" % (k, v))
    outfile.close()
    logfile.write("END\n")

        



