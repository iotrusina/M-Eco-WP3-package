import sqlite3


class DB(object):
    
    last_id = None
    
    @classmethod 
    def initDB(cls):
        sql = """
        drop table feeds;
        create table if not exists feeds(id primary key,type,name,url,update_time,last_update,cachefile,cache_type,output_scheme,map_rules);
        
        """
        cls.query(sql)
     
    @classmethod            
    def query(cls,querry, values):
        #print querry, values
        con = sqlite3.connect("webrss.db3");
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(querry, values)
        con.commit()
        a = cur.fetchall()
        cls.last_id = cur.lastrowid
        con.close()
        return a 
    
    

