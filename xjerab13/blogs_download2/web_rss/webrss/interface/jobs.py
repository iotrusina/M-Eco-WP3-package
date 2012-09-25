import cherrypy
from mako.lookup import TemplateLookup


lookup = TemplateLookup(directories = ['interface'])

class MyScheduler(object):

    @cherrypy.expose
    def index(self):
        pass