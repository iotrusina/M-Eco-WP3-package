import cherrypy
from webrss.model.feed import Feed
from mako.lookup import TemplateLookup


lookup = TemplateLookup(directories = ['interface'])

class DBView(object):
    
    @cherrypy.expose
    def index(self):
        items = Feed.findAll()
        tmpl = lookup.get_template("database.html")
        return tmpl.render(items = items, pgname="db")
        
    @cherrypy.expose
    def add(self, type, name, url):
        a = {"id":None,
             "type": type,
             "name": name,
             "url": url,
             "update_time":None,
             "last_update":None,
             "cache_file":None,
             "cache_type":None,
             "output_scheme":None,
             "map_rules":None,
             "logon":None,
             "password":None
                  }
        q = Feed(**a)
        q.save()
        