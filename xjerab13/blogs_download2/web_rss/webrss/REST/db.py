import cherrypy
from cherrypy.lib.cptools import accept
from webrss.model.feed import Feed
try:
    import json
except:
    import simplejson as json

class DbRESTService(object):
    
    def __init__(self,controler):
        self.cntrl = controler;
    
    exposed = True
    def GET(self, item_id= None):
        r = []
        if item_id:
            f = Feed.findById(item_id)
            r = f.getSelfAsDict()
        else:
            f = Feed.findAll()
            for i in f:
                r.append(i.getSelfAsDict())
        return json.dumps(r)
        pass
    
    def POST(self, type, name, url, utime, login = None, passwd = None):
        a = {"id":None,
             "enable": 0,
             "type": type,
             "name": name,
             "url": url,
             "update_time":int(utime),
             "last_update":0,
             "cache_data":0,
             "cache_type":None,
             "output_scheme":None,
             "map_rules":None,
             "logon":login,
             "password":passwd
                  }
        q = Feed(**a)
        q.save()
        #if enable == "1":
        #    self.cntrl.addJob(q)
        cherrypy.response.status = '201 Created'
        
    
    def PUT(self, id, **kw):
        f = Feed.findById(id)
        f.updateSelf(**kw) 
        f.save()
        self.cntrl.updateJob(f)
        
    
    def DELETE(self, item_id):
        self.cntrl.removeJob(item_id);
        f = Feed.findById(item_id)
        f.delete()
        cherrypy.response.status = '204 No Content'
        
    