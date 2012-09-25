import feedparser
from xml.etree import ElementTree
from xml.dom import minidom

from webrss.model.feed import Feed
from webrss.download import getDataFrom
from webrss.mapping import Mapper
import time
from htmlentitydefs import name2codepoint
import re



class BaseDownloader(object):
    
    prules = {}
    
    def __init__(self):
        self.dbfeed = None
        self.feed = None
        self.item = None
        pass
        
    def update_feed(self, raw_feed):
        return
    
    
    def parseFeed(self, dbfeeditem, feed_data = None):
        #feed_data = getDataFrom(self.dbfeed.url, self.dbfeed.logon, self.dbfeed.password)
        self.dbfeed = dbfeeditem
        if not feed_data:
            #feed_data = getDataFrom(self.dbfeed.url, self.dbfeed.logon, self.dbfeed.password)
            return None
        
            
        
        raw_feed = feedparser.parse(feed_data)
        self.update_feed(raw_feed)
        self.feed = raw_feed.feed
        
        maper = Mapper(self.dbfeed)
        maper.loadMapping()
        maper.loadScheme()
        root = ElementTree.Element(maper.schema_root.tag)
        
        old_timestamp = self.dbfeed.cache_data
        timestamp = old_timestamp
        new_timestamp = old_timestamp
        cntr = 0
        for self.item in raw_feed.entries:
            #self.item = item
            if self.item.has_key("updated_parsed"):
                timestamp = time.mktime(self.item.updated_parsed) 

                if new_timestamp < timestamp:
                    new_timestamp = timestamp
                if old_timestamp >= timestamp:
                    continue
            
            item = ElementTree.Element(maper.schema_container.tag)
            for t in maper.schema:
                text = None
                node_args = {}
                
                if self.__class__.prules.has_key(t.xpath):
                    i = self.__class__.prules[t.xpath]
                    if i["text"]:
                        fname = i["text"]["func_name"]
                        args = i["text"]["args"]
                        ftype = i["text"]["functype"]
                        if ftype == "static":
                            text = args
                        else:
                            text = getattr(self, fname)(args) if len(args) > 0 else getattr(self, fname)()  
                    
                    for at in i["attr"]:
                        fnc = getattr(self,at["func_name"])
                        if len(at["args"]) > 0:
                            node_args[at["name"]] = fnc(at["args"])
                        else:
                            node_args[at["name"]] = fnc()
                        
                    
                    self.build_xpath(item, t.xpath, text = text, args = node_args)
            root.append(item)
            cntr = cntr + 1
        #self.indent(root)
        #return ElementTree.tostring(root, 'utf-8')
        if cntr > 0:
            self.dbfeed.cache_data = new_timestamp
            rough_string = ElementTree.tostring(root, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            return reparsed.toprettyxml(indent="  ", encoding="UTF-8" )
        else:
            return None
        
    def build_xpath(self,node, path, text = None, args = {}):
        components = path.split("/")
        if components[0] == node.tag:
            components.pop(0)
        while components:
            component = components.pop(0)
            for child in list(node):
                if component == child.tag:
                    node = child
                    break
            else:
                if len(components) >= 1:
                    new_item = ElementTree.Element(component)
                    node.append(new_item)
                    node = new_item
                else:
                    new_item = ElementTree.Element(component, args)
                    if text:
                        new_item.text = text
                    node.append(new_item)
                    node = new_item
        
    def getItemFromFeedItem(self,args):
        parg = args.split(".")
        #print parg
        text = getattr(self,parg[0])[parg[1]]
        return text


    def getIsoDateTime(self, parsed_date = None):
        if parsed_date:
            parsed_date = self.getItemFromFeedItem(parsed_date)
            return time.strftime("%Y-%m-%dT%H:%M:%S",parsed_date)
        else:
            return time.strftime("%Y-%m-%dT%H:%M:%S")
        
    def indent(self, elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
                
    def unescape(self,text):
        def fixup(m):
            text = m.group(0)
            if text[:2] == "&#":
                # character reference
                try:
                    if text[:3] == "&#x":
                        return unichr(int(text[3:-1], 16))
                    else:
                        return unichr(int(text[2:-1]))
                except ValueError, e:
                    print e
                    pass
            else:
                # named entity
                try:
                    text = unichr(name2codepoint[text[1:-1]])
                except KeyError, e:
                    print e
                    pass
            return text # leave as is
        return re.sub("&#?\w+;", fixup, text)
                
    
    