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
    'item/guid': {   'attr': [],
                     'text': {   'args': '',
                                 'func_name': 'get_item_guid_text',
                                 'functype': 'userfunc'}},
    'item/lang': {   'attr': [],
                     'text': {   'args': 'item.iso_language',
                                 'func_name': 'getItemFromFeedItem',
                                 'functype': 'buildin'}},
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
        return "TV:" + self.getItemFromFeedItem("item.guid")
        
    def get_item_source_text(self):
        return self.dbfeed.url
        
    def get_item_section_text(self):
        return urlparse.urlparse(self.dbfeed.url).netloc.split(".")[-2]
        
    def get_item_text_text(self):
        link = self.getItemFromFeedItem("item.xmllink")
        xml_file = getDataFrom(urlparse.urljoin(self.dbfeed.url, urlparse.urlparse(link).path), self.dbfeed.logon, self.dbfeed.password)
        #writeToFile(xml_file, link.split("/")[-1], os.path.join("rss_backup","sail","xmls"), ".xml", timestamp=True)
        tree = ElementTree.fromstring(xml_file)
        text = ""
        for node in tree.getiterator('word'):
            if node.text is not None:
                text += "".join([a+" " for a in node.text.split()])
        text = text.replace(" .",".")
        text = " ".join(text.split())
        return text
        