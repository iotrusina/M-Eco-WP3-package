from dbsqlite import DB


class DatabaseObject(object):
    db_columns = []
    
    def __init__(self, **kwords):
        for name, value in kwords.items():
            if not name in self.__class__.db_columns:
                #raise KeyError("Unknown column")
                pass
            else:
                setattr(self, name, value)
            
        
    @classmethod
    def findBySQL(cls, sql, data):
        result_set = DB.query(sql, data)
        result_list = []
        for item in result_set:
            result_list.append(cls.instantiate(item))
        return result_list
    
    @classmethod
    def findById(cls, item_id):
        sql = """SELECT * FROM %s WHERE id=?""" %(cls.__name__)
        qq = cls.findBySQL(sql, (int(item_id),))
        return qq[0]
        pass
    
    @classmethod
    def findAll(cls):
        sql = """SELECT * FROM %s""" % (cls.__name__)
        return cls.findBySQL(sql, [])
    
    @classmethod    
    def instantiate(cls, data):
        newobject = cls()
        for i in range(len(cls.db_columns)):
            setattr(newobject, cls.db_columns[i], data[cls.db_columns[i]])
        return newobject
    
    
    
    
    def save(self):
        if self.id:
            self.update()
        else:
            self.create()
    
    def create(self):
        columns = ",".join(self.__class__.db_columns)
        values = [getattr(self, x) for x in self.__class__.db_columns]
        nvalues = ",".join(["?"]*len(values))
        sql = """INSERT INTO %s (%s) values(%s)""" % (self.__class__.__name__,columns,nvalues)
        DB.query(sql, values)
        x = DB.last_id
        self.id = x 
        
    
       
    def update(self):
        columns = [t+"=?" for t in self.__class__.db_columns[1:]]
        columns = ",".join(columns)
        
        values = [getattr(self, x) for x in self.__class__.db_columns[1:]]
        values.append(self.id)
        sql = """UPDATE %s set %s where id=?""" % (self.__class__.__name__,columns) 
        
        DB.query(sql, values)
    
    def delete(self):
        sql = """DELETE FROM %s WHERE id=?""" % (self.__class__.__name__)
        DB.query(sql, (self.id,))
        


