from hashlib import sha256
import shelve
import logging

class SimpleCache(object):
    def __init__(self):
        #self._cache = {}
        self._cache = shelve.open("netdoctor.cache", writeback=True)
        
    def __del__(self):
        self._cache.close()
        
    def isCached(self, item):
        url = item["url"]
        com = item["comments"]
        #print url,
        #print " cached ",
        
        if self._cache.has_key(url.encode("utf-8")):
            if len(self._cache[url.encode("utf-8")]) < com:
                #print "FALSE"
                logging.debug("Entry new found in the page - %s", url)
                return False
            else:
                #print "TRUE"
                logging.debug("Alreadz cached this has been - %s", url)
                return True
        else:
            #print "FALSE"
            logging.debug("Page new found i on site the - %s ",url)
            return False

    
    def cache(self, url, itemList):
        dataToStore = []
        hashlist = []
        if self._cache.has_key(url.encode("utf-8")):
            hashlist = self._cache[url] 
        for item in itemList:
            hash = sha256(item["text"].encode("utf-8")).hexdigest()
            if not hash in hashlist:
                hashlist.append(hash)
                item["guid"] = hash

                dataToStore.append(item)
        self._cache[url.encode("utf-8")] = hashlist
        return dataToStore
                
    
    
        
        


