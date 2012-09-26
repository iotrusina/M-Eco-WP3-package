import sqlite3
import logging
 
log = logging.getLogger("blog_download")

class dbcache:
    def __init__(self, cachename):
        self.cachename = cachename
        try:
            self.conn = sqlite3.connect(self.cachename)
            log.info("Opening database %s",self.cachename)
        except sqlite3.OperationalError: # Can't locate database file
            log.critical("nepodarilo se otevrit sql databazi")
            exit(1)
        self.cursor = self.conn.cursor()
 
    def createDatabase(self):
        cmd = "CREATE TABLE IF NOT EXISTS guidcache(guid VARCHAR(64))"
        #print cmd
        self.cursor.execute(cmd)
        self.conn.commit()
 
    def insertValue(self, guid):
        cmd = """INSERT INTO guidcache(guid) VALUES("%s")""" % (guid)
        #print "Inserting", guid+"..."
        self.cursor.execute(cmd)
 
        self.conn.commit()
 
    def getValue(self, guid):
        songDict = []
        cmd = """SELECT * FROM guidcache WHERE guid == "%s" """ %(guid)
        self.cursor.execute(cmd)
        results = self.cursor.fetchall()
        for song in results:
            songDict.append(song)
 
        return songDict
 
    def close(self):
        'Closes the connection to the database'
        if self.conn:
            log.info("Closing database")
            self.conn.commit() # Make sure all changes are saved
            self.conn.close()
        
    def __del__(self):
        self.close()

#if __name__ == '__main__':
#    db = dbcache("c:\\mydb")
#    db.createDatabase()
#    #qq = ["netdoktor:b04c984322d67ae51d8ef83439bff681a23d90b25716696b519c9b6ea4a2f145","netdoktor:3cb758ac1c93914c79c2d9bd5ae9e92149a04049e9950c0baf146cd9147fba32"]
#    #db.insertSongs(qq)
#    aa = db.getValue("netdoktor:")
#    print aa
#    db.closeHandle()
    
