import cherrypy
import os

from webrss.interface import Root, error_page_404
from webrss.REST.db import DbRESTService
from webrss.controler import Core
from webrss.REST import RESTService
from webrss.REST.control import ControlRESTService
import md5
from ConfigParser import RawConfigParser



current_dir = os.path.dirname(os.path.abspath(__file__))
def get_ulist():
    ini_parser = RawConfigParser()
    ini_parser.read("userlist.ini")
    a = ini_parser.items("default")
    qq = dict((y, x) for x, y in a)
    return qq

def encrypt_pw(pw):
    return pw

def main():
    ctrl = Core(name="core")
    ctrl.loadJobs()
    
    cherrypy.config.update("web_rss.ini")
    
    cherrypy.config.update({'error_page.404': error_page_404})
    
    #cherrypy.config.update({'server.socket_host': '147.229.205.40', 'server.socket_port': 8090, 'server.thread_pool': 4, 'log.screen': True})
    
    rest_service = RESTService()
    rest_service.db = DbRESTService(ctrl)
    rest_service.ctrl = ControlRESTService(ctrl)
    
    cherrypy.tree.mount(rest_service, "/api/", config = {'/':{'request.dispatch':cherrypy.dispatch.MethodDispatcher()}})
    
    conf = {
        '/static':
        { 'tools.staticdir.on':True,
          'tools.staticdir.dir':current_dir + "/static"
        },
          
        '/': {'tools.basic_auth.on': True,
              'tools.basic_auth.realm': 'athena3.fit.vutbr.cz',
              'tools.basic_auth.users': get_ulist,
              'tools.basic_auth.encrypt': encrypt_pw}  
       
    }
    
    cherrypy.engine.subscribe("stop", ctrl.stop)
    ctrl.start()
    cherrypy.quickstart(Root(ctrl), config = conf)
    
    
if __name__ == '__main__':
    main()
