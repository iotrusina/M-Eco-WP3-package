from xml.dom.minidom import Document
from xml.dom import Node
from urlparse import urlparse
from bdllib.pubmod import feedparser
import time
import logging
from bdllib.download import getDataFrom
from bdllib.shared_func import toUnicode, writeToFile
import os


log = logging.getLogger("blog_download")


class XmlGenerator(object):
    '''Base class for modules that downloading data via RSS/atom'''
    def __init__(self,  folder, cache = None, guid = "guid_preffix"):
        self.cache = cache
        self.folder = folder #output folder
        self.guid_prefix = guid
        self.handle_url = None  #feed url
        self.doc = Document() #xml generator
        self.was_error = False
        self.next_handler = None
        self.username = None
        self.password = None
        self.item_list = self.gen_item_list()
        self.makeBackup = False
        
        
    def registerNextHandler(self, handler):
        '''Register next item in responsibility chain'''
        self.next_handler = handler
        
    def work(self, item):
        '''Method that doign main work.'''
        url = item["url"]
        if url == self.handle_url or self.handle_url == None:
            self.username = item["login"]
            self.password = item["passwd"]
            self.process(url)
        else:
            return self.next_handler.work(item)
        
    
    def gen_item_list(self):
        #create list for generating final xml document
        item_list = {}
        tag_functions = [x for x in dir(self) if x.startswith("tag_")] 
        for f in tag_functions:
            item_list[f[4:]] = getattr(self,f)()
        return item_list
        
    
    def update_feed(self, feed, url):
        '''Add static data to feed dict'''
        feed["feed"]["source"] = url
        feed["feed"]["section"] = urlparse(url).netloc.split(".")[-2]

        
    def process(self, url):
        '''Download feed, process and create output'''
        content = getDataFrom(url, self.username, self.password)
        self.was_error = False
        self.doc = Document()
        #parsing feed
        feed = feedparser.parse(content)
        #if zero entries, no job appeared
        if len(feed.entries) <= 0:
            log.error("No Entries found in %s, you sure it is RSS or atom feed?", url)
            return None;
        
        #add static data to feed
        self.update_feed(feed , url)
        
        #create root tag
        t_results = self.doc.createElement("results")
        self.doc.appendChild(t_results)
        item_cnt = 0
        
        timestamp = None
        if self.cache:
            timestamp = self.cache.loadFromCache(url)
        new_stamp = timestamp
                
        #print "timestamp ",
        #print new_stamp
            
        #walk over parsed feed, minning data and create final xml
        for _c_ in range(len(feed.entries)):
            t_item = self.doc.createElement("item")
            try:
                #chceck feed item publication date, save only newer items
                if new_stamp < feed.entries[_c_].date_parsed:
                    new_stamp = feed.entries[_c_].date_parsed
                if timestamp >= feed.entries[_c_].date_parsed:
                    continue
            except:
                pass
            
            #walking over xml tag and their values
            for tag,value in self.item_list.items():
                path, func, req = value
                data = None
                
                if path is not None:
                    try:
                        f = feed
                        for key in path:
                            # _C_ as counter, mean number
                            if key == "_C_":
                                f = f[_c_]
                            else:
                                f = f[key]
                        data = f
                    except:
                        pass
                        

                #data postprocessing 
                if func is not None:
                    data = func(data) 
                    
                if req and data is None:
                    log.error("Nenalezena data pro tag %s", tag)
                    self.was_error = True
                if data is None:    
                    data = ""
                
                child = self.doc.createElement(tag) 
                 
                if isinstance(data, basestring):
                    data = self.doc.createTextNode(toUnicode(data))
                    
                if isinstance(data, Node):
                    child.appendChild(data)
                elif isinstance(data, dict):
                    for id, data in data.items():
                        child.setAttribute(id,data)
                     

                
                t_item.appendChild(child)
                t_results.appendChild(t_item)
            item_cnt += 1
        
        if item_cnt > 0:
            #print "new stamp "
            #print new_stamp
            self.writeWrapper(urlparse(url).netloc.split(".")[-2])
            if self.cache:
                self.cache.storeToCache(url,new_stamp)
            if self.makeBackup:
                writeToFile(content, "RSS_Sail_", os.path.join("rss_backup","sail"), ".xml", timestamp=True)
            
        else:
            log.debug("Nothing new in feed - %s " , url)
            return 

    def writeWrapper(self, name):
        '''wrapping save function'''
        ext = ".err" if self.was_error else ".xml"
        msg = writeToFile(content = self.doc.toprettyxml(indent="  ", encoding="UTF-8"),
                    filename = name,
                    folder = self.folder,
                    extension = ext,
                    timestamp = True
                    )
        log.info(msg)

    
        
    def tag_timestamp(self):
        path = None
        func = lambda x: time.strftime("%Y-%m-%dT%H:%M:%S")
        req = True
        return path, func, req
        
        
    def tag_guid(self):
        path = ["entries" ,"_C_" ,"id"]
        func = lambda x: self.guid_prefix+x if x else None
        req = True
        return path, func, req 
        
    
    def tag_section(self):
        path = ["feed", "section"]
        func = None
        req = True
        return path, func, req 
        
        
    def tag_source(self):
        path = ["feed", "source"]
        func = None
        req = False
        return path, func, req 
        
    
    def tag_lang(self):
        path = ["feed" ,"language"]
        func = lambda x: x.split("-")[0] if x else None
        req = True
        return path, func, req 
    
    def tag_link(self):
        path = ["entries" ,"_C_" ,"link"]
        func = None
        req = False
        return path, func, req
    
    def tag_pubDate(self):
        path = ["entries" ,"_C_" ,"date_parsed"]
        func = lambda x: time.strftime("%Y-%m-%dT%H:%M:%S",x) if x else None
        req = False
        return path, func, req
    
    def tag_title(self):
        path = ["entries" ,"_C_" ,"title"]
        func = None
        req = False
        return path, func, req
    
    def tag_text(self):
        path = ["entries" ,"_C_" ,"description"]
        func = None
        req = True
        return path, func, req
    
    def tag_author(self):
        path = ["entries","_C_","author_detail","name"]
        func = self.author_content
        req = True
        return path, func, req
    
    def author_content(self, data):
        t_name = self.doc.createElement("name")
        if data:
            t_name.appendChild(self.doc.createTextNode(data))
        return t_name
    
    
    
    