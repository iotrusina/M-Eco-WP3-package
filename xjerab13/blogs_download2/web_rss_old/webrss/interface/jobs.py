import cherrypy
from mako.lookup import TemplateLookup

lookup = TemplateLookup(directories = ['interface'])

class MyScheduler(object):

    @cherrypy.expose
    def index(self):
        tmpl = lookup.get_template("test.html")
        return tmpl.render(pgname="jobs")