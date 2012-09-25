from bdllib.pubmod import argparse
from bdllib.settings import loadSettings
from bdllib.exceptions import SettingsSectionNotFound
from bdllib.shared_func import makePath, createFolderStruc
from bdllib.moduleloader import ModuleHandler
from bdllib.baseclass.xmlgen import XmlGenerator
import csv, sys
from bdllib.timer import Timer
from bdllib.cache import CacheHandler
import logging
import os
from logging.handlers import TimedRotatingFileHandler



#global logging handler
log = None

class RssDownloader(object):
    '''Main class '''
    
    def __init__(self):
        #settings file
        self.settingsFile = "settings/rss_settings.ini"
        #default settings, used if data werent in textfile/command line
        self.settings = {
            "update_time":0, #pause in minutes betweed updates, if 0 program ends after one loop
            "input_file":None, 
            "output_folder":"rss_output",
            "guid_tag":'RSS:', #prefix for guid tag
            "logging":False,  #enable, disable logging
            "log_level":None, #specifying logging level
            "log_file":'rss.log',
            "log_folder":'logs',
            "use_cache":False,  #persistent some data
            
        }
        #worker manage all modules thats doing some work
        self.worker = None
        self.listOfUrls = []
        self.cache = None
    
    
    def setLogging(self, name):
        '''Setting loggin depends on settings.
        
         Keyword arguments:
         name - logging session name
         
        '''
        
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
        
        #rotating log file on midnight for 14 days
        handler = TimedRotatingFileHandler(log_file, when='midnight',interval = 1, backupCount=14)
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
        
        if self.settings["use_cache"]:
            self.cache = CacheHandler() #create cache object

            
        
        self.worker = ModuleHandler()  # create mpdule handler
        self.worker.loadModulesFrom("rss_modules", "rss_")  #and load what we need
        #chain of responsibility pattern
        self.worker.createChainOfInstances(XmlGenerator,
                                            folder = self.settings["output_folder"],
                                            cache = self.cache,
                                            guid = self.settings["guid_tag"]
                                           )
        self.loadInputFile()
        
    def loadSettingsFromCmd(self):
        cmd_parser = argparse.ArgumentParser(description = 'RSS downloader', prog = 'rssdownloader', prefix_chars = '-')
        cmd_parser.add_argument('-u', '--url', nargs = "*", help = 'URL address for download and parsing', metavar = 'URL', dest = "listOfUrls")
        cmd_parser.add_argument('-o', '--output', help = 'set destination folder', metavar = 'FOLDER', dest = "output_folder")
        cmd_parser.add_argument('-i', '--infinite', help = 'infinite program loop, wait time is TIME' , metavar = 'TIME' , type = int, dest = "update_time")
        cmd_parser.add_argument('-f', '--file', help = 'file with list of urls', dest = "input_file")
        cmd_parser.add_argument('-s', '--section' , help = 'use section in settings.ini for settings load' , default = 'default')

        arguments = vars(cmd_parser.parse_args())
        
        if arguments["section"]:
            self.loadSettingsFromFile(arguments["section"])

        
        for key in self.settings.keys():
            if arguments.has_key(key) and arguments[key] is not None:
                tmp = arguments[key]
                self.settings[key] = tmp

        if arguments["listOfUrls"]:
            log.debug("%d urls loaded from cmd", len(arguments["listOfUrls"]))
            for url in arguments["listOfUrls"]:
                if not url.startswith('http://'):
                    url = 'http://' + url
                dct = {
                    "url":url,
                    "login":None,
                    "passwd":None,
                    "timestamp":0
                }
            self.listOfUrls.append(dct)
            
    def loadBothSettingsAndMerge(self):
        self.loadSettingsFromFile()
        self.loadSettingsFromCmd()
            
    def run(self):
        '''Create and run timer'''
        timer = Timer(self.settings["update_time"])
        timer.addFunction(self.update)
        log.debug("*************Starting main loop***************\n\n")
        timer.start()
        
    
    def update(self):
        '''Main working function, caled from Timer'''
        log.info("Start update feeds!")
        
        if self.cache:
            self.cache.createPersistenCache("rss_timestamps")
        
        for i in self.listOfUrls:
            self.worker.work(item = i)
        
        if self.cache:
            self.cache.closeCache()
        log.info("Feeds update complete.\n")
        
    def loadInputFile(self):
        '''Load csv file with urls, usernames and passwords'''
        if self.settings["input_file"]:
            try:
                path = makePath(self.settings["input_file"])
                f = open(path, 'rt')
                reader = csv.DictReader(f)
                i = 0
                for row in reader:
                    if not row["url"].startswith('http://'):
                        row["url"] = 'http://' + row["url"]
                    row["timestamp"] = (0,0,0,0,0,0,0,0,0)
                    self.listOfUrls.append(row)
                i +=1
                f.close()
                log.debug("%d urls loaded from file", i)
               
            except IOError , e:
                sys.exit('File %s IOError: %s' % (self.settings["input_file"], e))
            except csv.Error, e:
                sys.exit('file %s, line %d: %s' % (self.settings["input_file"], reader.line_num, e))
        

if __name__ == '__main__':
    rssd = RssDownloader()
    rssd.loadSettingsFromFile()
    rssd.initAndLoadBySettings()
    rssd.run()
    
    
    
    
    
    
