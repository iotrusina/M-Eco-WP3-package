import cherrypy
from cherrypy.lib.cptools import accept
from webrss.model.feed import Feed
try:
    import json
except:
    import simplejson as json

class DbRESTService(object):
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
    
    def POST(self, type, name, url):
        a = {"id":None,
             "type": type,
             "name": name,
             "url": url,
             "update_time":3600,
             "last_update":0,
             "cache_file":None,
             "cache_type":None,
             "output_scheme":None,
             "map_rules":None,
             "logon":None,
             "password":None
                  }
        q = Feed(**a)
        q.save()
        cherrypy.response.status = '201 Created'
        
    
    def PUT(self):
        pass
    
    def DELETE(self, item_id):
        f = Feed.findById(item_id)
        f.delete()
        cherrypy.response.status = '204 No Content'
        
    