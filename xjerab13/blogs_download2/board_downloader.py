import os
import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from bdllib.shared_func import makePath, createFolderStruc
from bdllib.settings import loadSettings
from bdllib.exceptions import SettingsSectionNotFound
from bdllib.moduleloader import ModuleHandler
from bdllib.timer import Timer


log = None

class BoardDownloader(object):
    def __init__(self):
        self.settingsFile = "settings/board_settings.ini"
        self.settings = {
            "update_time":0,
            "output_folder":"board_output",
            "guid_tag":'board:',
            "logging":False,
            "log_level":None,
            "log_file":'board.log',
            "log_folder":'logs',

            
        }
        self.worker = None
        self.cache = None

    
    def setLogging(self, name):
        global log
        LEVELS = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'critical':logging.CRITICAL,
        }

        loglevel = LEVELS.get(self.settings["log_level"], logging.NOTSET)
        
        logdir = makePath(self.settings["log_folder"])
        createFolderStruc(logdir)
        
        log_formatter = logging.Formatter('%(levelname)s: (%(asctime)-15s) - %(message)s')
        log_file = os.path.join(logdir, self.settings["log_file"])
        
        handler = TimedRotatingFileHandler(log_file, when='midnight',interval = 1, backupCount=14)
        #handler = RotatingFileHandler(log_file, maxBytes=1*1024*1024, backupCount=500)
        handler.setFormatter(log_formatter)
        
        log = logging.getLogger(name)
        log.propagate = False
        
        log.addHandler(handler)
        log.setLevel(loglevel)
       
    def loadSettingsFromFile(self, section = "default"):
        try:
            loadSettings(self.settings, self.settingsFile, "default")
        except SettingsSectionNotFound,e:
            print e
            exit() 
            
    def initAndLoadBySettings(self):
        self.setLogging("blog_download")
        log.disabled = not self.settings["logging"] 
        
        self.worker = ModuleHandler()
        self.worker.loadModulesFrom("board_modules", "board_")
        self.worker.createListOfInstances(folder = self.settings["output_folder"]
                                          )
    
        
    def run(self):
        timer = Timer(self.settings["update_time"])
        timer.addFunction(self.update)
        log.debug("*************Starting main loop***************\n\n")
        timer.start()
        
    
    def update(self):
        log.info("Start crawling boards!")
        
        self.worker.work()
       
        log.info("Crawling complete.\n")
    
    
if __name__ == '__main__':
    try:
        bd = BoardDownloader()
        bd.loadSettingsFromFile()
        bd.initAndLoadBySettings()
        bd.run()
    except Exception,e:
        print e    
        log.critical("Some error again %s", e)
        log.exception("Some exception again")
    
