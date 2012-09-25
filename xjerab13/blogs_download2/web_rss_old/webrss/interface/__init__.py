import cherrypy

from mako.lookup import TemplateLookup
from mako.template import Template
from mako import exceptions
from webrss.analyzer import PageAnalyzer
from webrss.interface.dbview import DBView
from webrss.interface.jobs import MyScheduler

try:
    import json
except:
    import simplejson as json


lookup = TemplateLookup(directories = ['interface'])


class Root(object):

    db = DBView()
    jobs = MyScheduler()
    
    def __init__(self, controler):
        self.ctrl = controler

    @cherrypy.expose
    def index(self):
        try:
            tmpl = lookup.get_template("index.html")
            return tmpl.render(pgname="main", jobs = self.ctrl.getJobs())
        except:
            return exceptions.html_error_template().render()    
    
    @cherrypy.expose
    def analyzeUrl(self, url, rtype):
        a = PageAnalyzer(url)
        response = []
        if rtype == "lnk":
            
            a.findLinks()
            response = a.getLinks()
        elif rtype == "a":
            a.findOtherLinks()
            response = a.getOtherlinks()

        cherrypy.response.headers['Content-Type'] = "application/json"
        return json.dumps(response)
     
    @cherrypy.expose   
    def analyze(self):
        tmpl = lookup.get_template("analyze.html")
        return tmpl.render(pgname="analyze")

   
    
    @cherrypy.expose
    def cc(self):
        return self.ctrl.status
    
    @cherrypy.expose
    def ccs(self):
        self.ctrl.start()
        return self.ctrl.status
    
    @cherrypy.expose
    def ccss(self):
        self.ctrl.stop()
        return self.ctrl.status
    
    @cherrypy.expose
    def ex(self):
        exit(0)
        


    
def error_page_404(status, message, traceback, version):
    tmpl = lookup.get_template("404.html")
    return tmpl.render()
    



