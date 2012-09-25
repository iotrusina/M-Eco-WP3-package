from entry import Entry
import psycopg2 # operations with PyGreSQL
import getpass
import logging

class Connection:
    '''Class enables connection, executing queries, etc on athena3 server.'''
    ONE_ENTRY_LOOP = 512

    def __init__(self):
        self._logger = logging.getLogger()
	self.connection = None
        self.cursor = None

    def connect(self, user, database, host, port, password=None):
	'Method creating connection to database'
	if password is None:
            password = getpass.getpass()
        dns = 'user=' + user + ' dbname=' + database + ' host=' + host + ' password=' + 'Cn7I8IwS2cnFg1KIUX2wPMFv6KoJS7fq' + ' port=' + str(port)
        self.connection = psycopg2.connect(dns)
        self.cursor = self.connection.cursor()

    def _query(self, query):
	'Metod aplying query on database'
	self.cursor.execute(query)

    def _commit(self):
        'Method commiting all finished operations'
        self.connection.commit()

    def save_result(self, id, result):
        if(result == -1):
            q = 'UPDATE documents SET _relevance=\'0\' WHERE id=\'' + str(id) + '\''
        else:
            result = int(result * 100)
            q = 'UPDATE documents SET _relevance=\'' + str(result) + '\' WHERE id=\'' + str(id) + '\''
        self._query(q)
        self._commit()

    def remove_entry(self, id):
        'Removes specific entry from database. Deletes also insatnce pointing to this entry. Entry is identifie by id.'
        delete_docs_querry = 'DELETE FROM documents WHERE id=\'' + str(id) + '\''
        delete_inst_querry = 'DELETE FROM instances WHERE item_id=\'' + str(id) + '\''
        self._query(delete_inst_querry)
        self._query(delete_docs_querry)
        self._commit()

    #TODO: yield only text and id!
    def entries(self, language, entry_count=None, entry_offset=0, where='TRUE'):
	'Method yields Entry objects from database. where must be sql safe!'
	if entry_count == None:
	    self._query('SELECT COUNT(*) FROM documents WHERE (source_id IN (SELECT id FROM sources_twitter)) AND (' + where + ') AND language=\'%s\'  AND _relevance=\'-1\''  % (language))
            result = self.cursor.fetchone()
	    entry_count = result[0]
	for offset in xrange(entry_offset, entry_offset + entry_count, self.ONE_ENTRY_LOOP):
	    # either random samples from database or one by one. Random seems to be better
            self._query('SELECT id, guid, text FROM documents WHERE (source_id IN (SELECT id FROM sources_twitter)) AND (' + where + ') AND language=\'%s\' AND _relevance=\'-1\'ORDER BY RANDOM() LIMIT %d' % (language, self.ONE_ENTRY_LOOP))
            result = self.cursor.fetchall()
	    for entry in result:
		yield Entry(id=entry[0], guid=entry[1], entry=entry[2], language=language)

    def get_all_entrys(self, language, where="TRUE"):
        self._query('SELECT COUNT(*) FROM documents WHERE (source_id IN (SELECT id FROM sources_twitter)) AND (' + where + ') AND language=\'%s\' AND _relevance=\'-1\'' % (language))
        result = self.cursor.fetchone()
        entry_count = result[0]
        for offset in xrange(0, entry_count, self.ONE_ENTRY_LOOP):
            self._query('SELECT id, guid, text FROM documents WHERE (source_id IN (SELECT id FROM sources_twitter)) AND (' + where + ') AND language=\'%s\' AND _relevance=\'-1\' LIMIT %d OFFSET %d' % (language, self.ONE_ENTRY_LOOP, offset))
            result = self.cursor.fetchall()
	    for entry in result:
		yield Entry(id=entry[0], guid=entry[1], entry=entry[2], language=language)

    def get_entry_by_id(self, id):
	'Methods returns Entry object according to id.'
	self._query('SELECT guid, text, language FROM documents WHERE id=\'%d\'' % (id))
        result = self.cursor.fetchone()
        if result:
            return Entry(id=id, guid=result[0], entry=result[1], language=result[2])
        else:
            return None

    def close(self):
	'Method closing connection to DB'
        self.cursor.close()
	self.connection.close()
