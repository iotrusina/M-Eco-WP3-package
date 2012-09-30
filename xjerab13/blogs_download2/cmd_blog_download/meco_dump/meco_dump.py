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
        self.filename = None
        self.lang = None
        self.path = ""
        
        
    def cmdInit(self):
        cmd_parser = argparse.ArgumentParser(description = 'meco database dump', prog = 'meco_dump', prefix_chars = '-')
        cmd_parser.add_argument('-f', '--from', help = 'start date', metavar = 'YYYY-MM-DD', dest = "date_from")
        cmd_parser.add_argument('-t', '--to', help = 'stop date' , metavar = 'YYYY-MM-DD' , dest = "date_to")
        cmd_parser.add_argument('-a', '--all', help = 'make dump of whole db', dest = "dump", action = "store_true", default = False)
        cmd_parser.add_argument('-y', help = 'make dump all events from yestreday', dest = "yesterday", action = "store_true", default = False)
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
        
        if arguments["yesterday"]:
            self.date_from = datetime.date.today() - datetime.timedelta(days=1)
            self.date_to = self.date_from.isoformat()
            self.date_from = self.date_to
            
            if self.filename is None:
                self.filename = "meco_dump_" + self.date_from + ".csv"
                
            
            return
        if arguments["date_from"] is not None and arguments["date_to"] is None:
            self.testDate(arguments["date_from"])
            self.date_from = arguments["date_from"]
            self.date_to = self.date_from
        
            if self.filename is None:
                self.filename = "meco_dump_" + self.date_from + ".csv"
                
            return
        
        if arguments["date_to"] is not None and arguments["date_from"] is not None:
            
            self.testDate(arguments["date_to"])
            self.testDate(arguments["date_from"])
        
            self.date_to = arguments["date_to"]
            self.date_from = arguments["date_from"]
            
            
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
        except ValueError:
            print "Ilegal date " + str(date)
            exit(1)
        
    
    def makePath(self, path):
        '''Creating absolute path based on program position in filesystem.'''
        if os.path.isabs(path):
            return path
        else:
            return os.path.join(sys.path[0], path)
          
    
    def database_dump(self):
        self.sordDates()
        path = self.makePath(self.path)
        if self.lang is not None:
            self.filename = self.lang + "_" + self.filename
        
        finalpath = os.path.join(path,self.filename)
        conn = psycopg2.connect(host='localhost', database='meco', user='meco', password='Cn7I8IwS2cnFg1KIUX2wPMFv6KoJS7fq')
        cursor = conn.cursor()

        query = "SELECT e.normalized_entity, doc.pubdate, count(e.normalized_entity) AS num "
        query += "FROM documents AS doc "
        query += "INNER JOIN sources AS s ON doc.source_id = s.id "
        query += "INNER JOIN instances AS i ON doc.id = i.item_id "
        query += "INNER JOIN entities AS e ON e.id = i.entity_id "
        query += "INNER JOIN enttypes AS ent ON e.enttype_id = ent.id "
        query += "WHERE s.normalized_section = 'twitter' AND ent.parent = 'MedicalCondition' "
        if self.lang is not None:
            query += " AND doc.language = '"+ self.lang + "'" 
        if self.date_from is not None and self.date_to is not None:
            query += " AND doc.pubdate BETWEEN '" + self.date_from + "' AND '" + self.date_to + "' "
        query += "GROUP BY e.normalized_entity, doc.pubdate "
        query += "ORDER BY doc.pubdate DESC"
            
        cursor.execute(query)
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close() 
        
        if len(rows) == 0:
            print "No rows found"
        
        f = open(finalpath,"w")
        for row in rows:
            line = str(row[0]) + "\t" + row[1].strftime("%Y%m%d") + "\t" + str(row[2]) + "\n"
            f.write(line)
        
        f.close()

    


def main():
    xx = mecoDump()
    xx.cmdInit()
    xx.database_dump()

if __name__ == '__main__':
    main()