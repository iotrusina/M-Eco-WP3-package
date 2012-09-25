import re
import hashlib
import urlparse
import copy
import time
from xml.etree import ElementTree
from webrss.downloaders import BaseDownloader
from webrss.download import getDataFrom
from BeautifulSoup import BeautifulSoup
from webrss.shared_func import writeToFile

class Downloader(BaseDownloader):
    prules = {   'item/author/name': {   'attr': [],
                            'text': {   'args': 'item.author',
                                        'func_name': 'getItemFromFeedItem',
                                        'functype': 'buildin'}},
    'item/guid': {   'attr': [],
                     'text': {   'args': '',
                                 'func_name': 'get_item_guid_text',
                                 'functype': 'userfunc'}},
    'item/lang': {   'attr': [],
                     'text': {   'args': '',
                                 'func_name': 'get_item_lang_text',
                                 'functype': 'userfunc'}},
    'item/link': {   'attr': [],
                     'text': {   'args': 'item.link',
                                 'func_name': 'getItemFromFeedItem',
                                 'functype': 'buildin'}},
    'item/pubDate': {   'attr': [],
                        'text': {   'args': 'item.updated_parsed',
                                    'func_name': 'getIsoDateTime',
                                    'functype': 'buildin'}},
    'item/section': {   'attr': [],
                        'text': {   'args': '',
                                    'func_name': 'get_item_section_text',
                                    'functype': 'userfunc'}},
    'item/source': {   'attr': [],
                       'text': {   'args': 'feed.link',
                                   'func_name': 'getItemFromFeedItem',
                                   'functype': 'buildin'}},
    'item/text': {   'attr': [],
                     'text': {   'args': 'item.description',
                                 'func_name': 'getItemFromFeedItem',
                                 'functype': 'buildin'}},
    'item/timestamp': {   'attr': [],
                          'text': {   'args': '',
                                      'func_name': 'getIsoDateTime',
                                      'functype': 'buildin'}},
    'item/title': {   'attr': [],
                      'text': {   'args': 'item.title',
                                  'func_name': 'getItemFromFeedItem',
                                  'functype': 'buildin'}}}

    def update_feed(self, raw_feed):
        new_entries = []
        #print feed["entries"]
        
        timestamp = self.dbfeed.cache_data
        
        
        for e in raw_feed["entries"]:
            if timestamp >= time.mktime(e.updated_parsed):
                continue 
            time.sleep(1)
            #print e["link"]
            page = getDataFrom(e["link"], self.dbfeed.logon, self.dbfeed.password)
            if page is None:
                continue
            soup = BeautifulSoup(page)
            div = soup.find(id = 'page')
            strongs = div.findAll("strong")
            content = []
            for c in strongs:
                title = c.next
                text = c.next.next.next
                content.append([title,text])
        
            c = 0
            guid = e.id
            for item in content:
                title, text = item
                new_item = None
                new_item = copy.deepcopy(e)
                new_item["id"] = str(c)+":"+ guid
                new_item["title"] = title
                new_item["description"] = text
                new_entries.append(new_item)
                c +=1
                if "<br/>" in text:
                    print "found!!!"
                    return
            
        raw_feed["entries"] = new_entries
        
    def get_item_guid_text(self):
        return "drfruehwein:" + self.getItemFromFeedItem("item.guid")
        
    def get_item_section_text(self):
        return urlparse.urlparse(self.dbfeed.url).netloc.split(".")[-2]
        
    def get_item_lang_text(self):
        return self.getItemFromFeedItem("feed.language").split("-")[0]
        