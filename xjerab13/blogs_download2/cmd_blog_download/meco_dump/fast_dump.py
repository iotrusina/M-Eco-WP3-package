import os
import sys
from site import makepath

try:
    import argparse
except Exception:
    from bdllib.pubmod import argparse
    
import psycopg2 
import datetime




class mecoDump():
    def __init__(self):
        self.date_from = None
        self.date_to = None
        self.dumpall = False
        self.rangedDump = False
        self.filename = None
        self.lang = None
        self.path = ""
        
        
    def cmdInit(self):
        cmd_parser = argparse.ArgumentParser(description = 'meco database dump', prog = 'meco_dump', prefix_chars = '-')
        cmd_parser.add_argument('-f', '--from', help = 'start date', metavar = 'YYYY-MM-DD', dest = "date_from")
        cmd_parser.add_argument('-t', '--to', help = 'stop date' , metavar = 'YYYY-MM-DD' , dest = "date_to")
        cmd_parser.add_argument('-a', '--all', help = 'make dump of whole db', dest = "dump", action = "store_true", default = False)
        cmd_parser.add_argument('-o', '--output', help = 'force default filename', dest = "filename", action = "store")
        cmd_parser.add_argument('-l', '--lang', help = 'set language', dest = "lang", action = "store")

        arguments = vars(cmd_parser.parse_args())

        self.dumpall = arguments["dump"]
        self.filename = arguments["filename"]
        self.lang = arguments["lang"]

        if self.dumpall:
            if self.filename is None:
                self.filename = "meco_full_dump.csv"
            return
        
        
            
            
        if arguments["date_from"] is not None and arguments["date_to"] is None:
            
            self.date_from = self.testDate(arguments["date_from"])
            self.date_to = self.date_from
        
            if self.filename is None:
                self.filename = "meco_dump_" + self.date_from + ".csv"
                
            return
        
        if arguments["date_to"] is not None and arguments["date_from"] is not None:
            
            self.date_to = self.testDate(arguments["date_to"])
            self.date_from = self.testDate(arguments["date_from"])
            
            self.rangedDump = True
            
            if self.filename is None:
                self.filename = "meco_dump_" + self.date_to + "_to_" + self.date_from + ".csv"
            
            return
        
        print "selector requied, use meco_dump --help for more info"
        exit(1)
        
    
    def sordDates(self):
        if self.date_from > self.date_to:
            xx = self.date_from
            self.date_from = self.date_to
            self.date_to = xx
        
        
    def testDate(self, date):
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
            return date
        except ValueError:
            print "Ilegal date " + str(date)
            exit(1)
        
    
    def makePath(self, path):
        '''Creating absolute path based on program position in filesystem.'''
        if os.path.isabs(path):
            return path
        else:
            return os.path.join(sys.path[0], path)
          
    def setDates(self, cursor):
        query = "SELECT min(pubdate), max(pubdate) FROM documents "
        if self.lang is not None:
            query += "WHERE = '"+ self.lang + "'" 
        cursor.execute(query)
        rows = cursor.fetchall()
        self.date_from = rows[0][1]
        self.date_to = rows[0][0]
        #print self.date_from, self.date_to
        
    
    def database_dump(self):

        
        
        
        path = self.makePath(self.path)
        
        if self.lang is not None:
            self.filename = self.lang + "_" + self.filename
            
        finalpath = os.path.join(path,self.filename)
        
        conn = psycopg2.connect(host='localhost', database='meco', user='meco', password='Cn7I8IwS2cnFg1KIUX2wPMFv6KoJS7fq')
        cursor = conn.cursor()

        rows = []
        
        if self.dumpall:
            self.setDates(cursor)
            
        self.sordDates()
        
        if self.dumpall or self.rangedDump:
            rows = self.range_query(cursor, self.lang, self.date_from, self.date_to)
        else:
            rows = self.single_query(cursor, self.date_from, self.lang)
         
        cursor.close()
        conn.close() 
        
        if len(rows) == 0:
            print "No rows found"
        
        f = open(finalpath,"w")
        for row in rows:
            line = str(row[0]) + "\t" + row[1].strftime("%Y%m%d") + "\t" + str(row[2]) + "\n"
            f.write(line)
        
        f.close()
        
    def range_query(self, cursor, lang, date_from, date_to):
        stop_date = datetime.datetime.strptime(date_from, "%Y-%m-%d")
        start_date = datetime.datetime.strptime(date_to, "%Y-%m-%d")
        oneday = datetime.timedelta(days = 1)
        output = []
        while(True):
            output += self.single_query(cursor, start_date.strftime("%Y-%m-%d"), lang) 
            start_date = start_date - oneday
            if start_date < stop_date:
                break
        return output
            
    
    def single_query(self, cursor, date = None, lang = None):
        print "single query for " + str(date) + " lang " + lang
        query = "SELECT e.normalized_entity, doc.pubdate, count(e.normalized_entity) AS num "
        query += "FROM documents AS doc "
        query += "INNER JOIN sources AS s ON doc.source_id = s.id "
        query += "INNER JOIN instances AS i ON doc.id = i.item_id "
        query += "INNER JOIN entities AS e ON e.id = i.entity_id "
        query += "INNER JOIN enttypes AS ent ON e.enttype_id = ent.id "
        query += "WHERE s.normalized_section = 'twitter' AND ent.parent = 'MedicalCondition' "
        if lang is not None:
            query += " AND doc.language = '"+ lang + "'" 
        if date is not None:
            query += " AND doc.pubdate = '" + date + "' "
        query += "GROUP BY e.normalized_entity, doc.pubdate "
        query += "ORDER BY doc.pubdate DESC"
            
        cursor.execute(query)
        return cursor.fetchall()
        
        pass
        

    


def main():
    xx = mecoDump()
    xx.cmdInit()
    xx.database_dump()

if __name__ == '__main__':
    main()