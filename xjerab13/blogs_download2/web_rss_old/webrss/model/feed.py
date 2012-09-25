from webrss.model import DatabaseObject

class Feed(DatabaseObject):
    db_columns = ["id","type","name","url","update_time","last_update","cache_file","cache_type","output_scheme","map_rules", "logon", "password"]
    
    def getSelfAsDict(self):
        r = {}
        for i in self.__class__.db_columns:
            r[i] = getattr(self, i)
        return r
            
        
        
    