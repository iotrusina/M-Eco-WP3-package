import shelve
import logging
import cPickle as pickle
import os


log = logging.getLogger("blog_download")


class _SimpleCache(object):
    ''' create simple dictionary cache'''
    def __init__(self, pathToCache = None ,persistent = False):
        self.persistence = persistent
        self.pathToCache = pathToCache
        self._cache = {}
        self.initCache()
        
    
    
        
    def initCache(self):
        '''init cache, try load from file if persistent'''
        if self.persistence:
            #self._cache = shelve.open(self.pathToCache, writeback=True)
            if os.path.exists(self.pathToCache):
                f = open(self.pathToCache, "rb")
                
                self._cache = pickle.load(f)
                f.close()
                
            log.debug("Create persistence cache - %s", self.pathToCache)
        else:
            log.debug("Create memory cache")
            
        
    
    def getContent(self,key):
        '''load and return data'''
        #print "content for key" + key
        if self._cache.has_key(key):
            #print self._cache[key]
            return self._cache[key]
        else:
            #print "None"
            return None
    
    
    def SetContent(self, key, data):
        #print key, data
        self._cache[key] = data
    
        
    def dumpCache(self):
        '''save cache to hdd as pickle'''
        if self.persistence:
            try:
                f = open(self.pathToCache, "wb")
                pickle.dump(self._cache, f, protocol=2)
                f.close()
                log.debug("Dumping cache to %s", self.pathToCache)
                #log.debug("cache: %s", self._cache)
            except IOError ,e:
                log.error("Cache dump failed: %s", e)

    
    def __del__(self):
        self.dumpCache()
        
            
        
    
    

    
    
    


