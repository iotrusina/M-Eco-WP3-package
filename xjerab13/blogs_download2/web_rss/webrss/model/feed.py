from webrss.model import DatabaseObject

class Feed(DatabaseObject):
    #db_columns = ["id","type","name","url","update_time","last_update","cache_file","cache_type","output_scheme","map_rules", "logon", "password"]
    db_columns = ["id", "enable", "backup","type", "name", "url", "update_time", "last_update", "cache_data","output_scheme","map_rules","logon", "password"]
    
    def getSelfAsDict(self):
        r = {}
        for i in self.__class__.db_columns:
            r[i] = getattr(self, i)
        return r
            
    def updateSelf(self, **kw):
        k = kw.keys()
        print kw,k
        if "enable" in k:
            self.enable = kw["enable"]
        if "name" in k:
            self.name = kw["name"]
            print "update name",self.name
        if "type" in k:
            self.type = kw["type"]
            print "update type",self.type
        if "url" in k:
            self.url = kw["url"]
            print "update url",self.url
        if "utime" in k:
            self.update_time = int(kw["utime"])
            print "update time",self.update_time
        if "login" in k:
            self.logon = kw["login"]
        if "passwd" in k:
            self.password = kw["passwd"]

    def updateFromJob(self, job):
        for i in self.__class__.db_columns:
            v = getattr(job, i)
            setattr(self, i, v)