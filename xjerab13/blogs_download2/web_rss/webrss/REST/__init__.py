from webrss.REST.control import ControlRESTService
from webrss.REST.db import DbRESTService



class RESTService(object):
    #db = DbRESTService()
    #ctrl = ControlRESTService()
    #expose = True
    
    def __init__(self):
        self.db = None
        self.ctrl = None