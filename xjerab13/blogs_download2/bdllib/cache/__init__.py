from bdllib.shared_func import makePath, createFolderStruc
import os
from bdllib.cache.simplecache import _SimpleCache
from hashlib import sha256



class CacheHandler(object):
    '''Cache adapter.'''
    def __init__(self, cacheFolder=".cacheFiles"):
        self._cache = None
        self.cacheFolder = makePath(cacheFolder) 
    
    
    def createMemoryCache(self):
        '''Create memory cache - dictionary.'''
        self._cache = _SimpleCache()
        pass
        
    def createPersistenCache(self, filename, ext = ".cache"):
        '''Create persistent cache - dict. On cache delete is stored as pickle on hdd.'''
        if not ext.startswith("."):
            ext = "." + ext
            
        if self._cache:
            self._cache.dumpCache()
        

        createFolderStruc(self.cacheFolder)
            
        path = makePath(os.path.join(self.cacheFolder,filename)+ext)
        self._cache = _SimpleCache(path, persistent = True)
           
        pass
    
    def createDbCache(self, filename, ext = ".db"):
        '''using dataabse as cachce'''
        if not ext.startswith("."):
            ext = "." + ext
            
        if self._cache:
            self._cache.dumpCache()
        

        createFolderStruc(self.cacheFolder)
            
        path = makePath(os.path.join(self.cacheFolder,filename)+ext)
        #self._cache = dbcache(path)
        #self._cache.createDatabase()
        
    
        
    def loadFromCache(self,key):
        
        return self._cache.getContent(key)
    
    def storeToCache(self, key , data):
        self._cache.SetContent(key, data)
    
    def closeCache(self):
        self._cache = None
    
    def appendData(self,key,data):
        cached = self._cache.getContent(key)
        if isinstance(cached, list):
            cached.append(data)
        else:
            cached = [cached]
            cached.append(data)
        self._cache.cache(key, cached)
    
    def getEntriesLen(self,key):
        data = self._cache.getContent(key)
        return data["allEntries"] if data else 0 

    def setEntriesLen(self,key, number):
        data = self._cache.getContent(key)
        #print "updating coms from " + str(data["allEntries"]) + "to " + str(number)
        data = data if data else {}
        data["allEntries"] = number
        self._cache.SetContent(key, data)
        
    def cacheAndReturnNew(self,key, itemlist):
        '''wrapper to cache data function, depends on cache type'''
        if isinstance(self._cache, _SimpleCache):
            return self.cacheAndReturnNewP(key, itemlist)
        elif isinstance(self._cache, dbcache):
            return self.cacheAndReturnNewD(itemlist)
     
    def cacheAndReturnNewP(self, key, itemList):
        '''cache item in persistent cache'''
        dataToStore = []
        cached = self._cache.getContent(key) 
        cached = cached if cached else {}
        hashlist = cached["content"] if cached.has_key("content") else []
        
        for item in itemList:
            hash = sha256(item["text"].encode("utf-8")).hexdigest()
            if not hash in hashlist:
                hashlist.append(hash)
                item["guid"] = "netdoktor:"+hash

                dataToStore.append(item)
        cached["content"] = hashlist
        self._cache.SetContent(key, cached)
        return dataToStore
    
    def cacheAndReturnNewD(self, itemList):
        '''cache item in database cache'''
        dataToStore = []
        for item in itemList:
            hash = sha256(item["text"].encode("utf-8")).hexdigest()
            hashlist = self._cache.getValue(hash)
            if not hashlist:
                hashlist.append(hash)
                item["guid"] = "netdoktor:"+hash
                self._cache.insertValue(hash)

                dataToStore.append(item)
            else:
                #print "DUP FILEEEEE"
                pass
        return dataToStore
    
    
        
        
    
        