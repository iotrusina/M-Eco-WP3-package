import cherrypy
import os

from webrss.interface import Root, error_page_404
from webrss.REST import DbRESTService
from webrss.controler import Core



current_dir = os.path.dirname(os.path.abspath(__file__))

def main():
    
    
    
    ctrl = Core(name="core")
    ctrl.loadJobs()

    cherrypy.config.update("web_rss.ini")
    
    cherrypy.config.update({'error_page.404': error_page_404})
    
    #cherrypy.config.update({'server.socket_host': '147.229.205.40', 'server.socket_port': 8090, 'server.thread_pool': 4, 'log.screen': True})
    
    rest_service = DbRESTService()
    
    cherrypy.tree.mount(rest_service, "/api/rest/", config = {'/':{'request.dispatch':cherrypy.dispatch.MethodDispatcher()}})
    
    conf = {
        '/static':
        { 'tools.staticdir.on':True,
          'tools.staticdir.dir':current_dir + "/static"
        },
            
       
    }
    
    cherrypy.engine.subscribe("stop", ctrl.stop)
    ctrl.start()
    cherrypy.quickstart(Root(ctrl), config = conf)
    
    
if __name__ == '__main__':
    main()
