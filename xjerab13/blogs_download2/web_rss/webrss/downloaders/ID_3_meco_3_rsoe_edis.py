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
                            'text': {   'args': '',
                                        'func_name': None,
                                        'functype': 'static'}},
    'item/georss': {   'attr': [   {   'args': '',
                                       'func_name': 'get_item_georss_attr_lon',
                                       'functype': 'userfunc',
                                       'name': 'lon'},
                                   {   'args': '',
                                       'func_name': 'get_item_georss_attr_lat',
                                       'functype': 'userfunc',
                                       'name': 'lat'}],
                       'text': None},
    'item/guid': {   'attr': [],
                     'text': {   'args': '',
                                 'func_name': 'get_item_guid_text',
                                 'functype': 'userfunc'}},
    'item/lang': {   'attr': [],
                     'text': {   'args': 'en',
                                 'func_name': None,
                                 'functype': 'static'}},
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
                       'text': {   'args': '',
                                   'func_name': 'get_item_source_text',
                                   'functype': 'userfunc'}},
    'item/text': {   'attr': [],
                     'text': {   'args': '',
                                 'func_name': 'get_item_text_text',
                                 'functype': 'userfunc'}},
    'item/timestamp': {   'attr': [],
                          'text': {   'args': '',
                                      'func_name': 'getIsoDateTime',
                                      'functype': 'buildin'}},
    'item/title': {   'attr': [],
                      'text': {   'args': 'item.title',
                                  'func_name': 'getItemFromFeedItem',
                                  'functype': 'buildin'}}}

    def update_feed(self, raw_feed):
        pass
        
    def get_item_guid_text(self):
        data = self.getItemFromFeedItem("item.content")
        text = ""
        for d in data:
            output  = re.compile('<code>(.*?)</code>', re.DOTALL |  re.IGNORECASE).findall(d.value)
            for t in output:
                text +=self.unescape(t.replace("&", "&"))
        return "rsoeedis:" + str(hashlib.sha224(text.encode("utf-8")).hexdigest())
        
    def get_item_source_text(self):
        return self.dbfeed.url
        
    def get_item_section_text(self):
        return urlparse.urlparse(self.dbfeed.url).netloc.split(".")[-2]
        
    def get_item_georss_attr_lon(self):
        return self.getItemFromFeedItem("item.georss_point").split(" ")[1]
        
    def get_item_georss_attr_lat(self):
        return self.getItemFromFeedItem("item.georss_point").split(" ")[0]
        
    def get_item_text_text(self):
        data = self.getItemFromFeedItem("item.content")
        text = ""
        for d in data:
            output  = re.compile('<code>(.*?)</code>', re.DOTALL |  re.IGNORECASE).findall(d.value)
            for t in output:
                text +=self.unescape(t.replace("&", "&"))
        return text
        