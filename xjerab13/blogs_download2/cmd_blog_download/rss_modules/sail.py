from bdllib.baseclass.xmlgen import XmlGenerator
from xml.etree import ElementTree
from urlparse import urlparse, urljoin
from bdllib.download import getDataFrom
from bdllib.shared_func import writeToFile
import os

class RSS_XmlGeneratorSail(XmlGenerator):

    def __init__(self, folder, cache, guid ):
        XmlGenerator.__init__(self, folder, cache, guid)
        self.handle_url = "http://webdemo.sail-labs.com/MediaMiningBasic/rss.jsp"
        self.guid_prefix = "TV:"
        self.makeBackup = True
        
        
    def define_update_dict(self):
        dict = {
        "guid":[["entries" ,"_C_" ,"id"] , lambda x: "TV:"+x],
        "text":[["entries","_C_"],"self.sail_labs_writer"],
        "lang":[["entries","_C_","iso_language"],None]
        } 
        return dict
    
    def tag_text(self):
        path = ["entries" ,"_C_" ,"xmllink"]
        func = self.text_creator
        req = True
        return path, func, req
        
    def tag_lang(self):
        path = ["entries","_C_","iso_language"]
        func = None
        req = True
        return path, func, req 
    
    
    def text_creator(self, link):
        xml_file = getDataFrom(urljoin(self.handle_url, urlparse(link).path), self.username, self.password)
        writeToFile(xml_file, link.split("/")[-1], os.path.join("rss_backup","sail","xmls"), ".xml", timestamp=True)
        tree = ElementTree.fromstring(xml_file)
        text = ""
        for node in tree.getiterator('word'):
            if node.text is not None:
                text += "".join([a+" " for a in node.text.split()])
        
        text = text.replace(" .",".")
        text = " ".join(text.split())
        return text
        
        
    

