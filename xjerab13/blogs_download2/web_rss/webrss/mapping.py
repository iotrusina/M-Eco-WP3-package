from xml.etree.ElementTree import iterparse
from xml.etree import ElementTree
import os
from webrss.shared_func import writeToFile



class struct(object):
    pass


class Mapper(object):
    

    def __init__(self, feed_item):
        self.feed = feed_item
        self.schema = []
        self.func_update = ""
        self.schema_root = None
        self.schema_container = None
        self.funcs={}
        self.imports = []
    
    
    def loadScheme(self):
        que = []
        scheme = self.feed.output_scheme
        map_file = self.feed.map_rules if self.feed.map_rules else ''
        
        if scheme == None:
            return
        filepath = os.path.join("schemas",scheme, "schema.xml")
        for (event, node) in iterparse(filepath, ['start', 'end']):
            if event == 'end':
                que.pop()
            if event == 'start':
                que.append(node.tag)
                if not list(node):
                    o = struct()
                    o.xpath = "/".join(que[1:])
                    o.tag = node.tag
                    o.desc = node.text
                    self.schema.append(o)
                else:
                    if len(que) == 1:
                        o = struct()
                        o.xpath = "/".join(que)
                        o.tag = node.tag
                        self.schema_root = o
                    elif len(que) == 2:
                        o = struct()
                        o.xpath = "/".join(que)
                        o.tag = node.tag
                        self.schema_container = o
    
    
    def loadMapping(self):
        scheme = self.feed.output_scheme
        map_file = self.feed.map_rules if self.feed.map_rules else ''
        if scheme == None:
            return
        
        filepath = os.path.join("schemas",scheme,map_file, "mapping.xml")
        
        f = open(filepath, 'rt')
        tree = ElementTree.parse(f)
        f.close()
        
        for node in tree.getiterator("item"):
            o = struct()
            o.text = None
            o.attr = []
            for_attr =  node.attrib.get('for')
            for subnode in list(node):
                if subnode.tag == "text":
                    t = struct()
                    t.functype = subnode.attrib.get("functype")
                    t.args = subnode.attrib.get("args")
                    t.func_name = subnode.text
                    o.text = t
                elif subnode.tag == "attr":
                    t = struct()
                    t.name = subnode.attrib.get("name")
                    t.functype = subnode.attrib.get("functype")
                    t.args = subnode.attrib.get("args")
                    t.func_name = subnode.text
                    o.attr.append(t)
            self.funcs[for_attr] = o
        
        self.func_update = tree.find("update_feed").text
        
        
    def loadMappingAsDict(self):   
        scheme = self.feed.output_scheme
        map_file = self.feed.map_rules
        if map_file == None:
            return
        
        filepath = os.path.join("schemas",scheme,map_file, "mapping.xml")
        
        f = open(filepath, 'rt')
        tree = ElementTree.parse(f)
        f.close()
        
        for node in tree.getiterator("item"):
            o = {}
            o["text"] = None
            o["attr"] = []
            for_attr =  node.attrib.get('for')
            for subnode in list(node):
                if subnode.tag == "text":
                    t = {}
                    t["functype"] = subnode.attrib.get("functype")
                    t["args"] = subnode.attrib.get("args")
                    t["func_name"] = subnode.text
                    o["text"] = t
                elif subnode.tag == "attr":
                    t = {}
                    t["name"] = subnode.attrib.get("name")
                    t["functype"] = subnode.attrib.get("functype")
                    t["args"] = subnode.attrib.get("args")
                    t["func_name"] = subnode.text
                    o["attr"].append(t)
            self.funcs[for_attr] = o
            
        self.func_update = tree.find("update_feed").text
        
        
    def saveSchema(self, feed_item, schema, data):
        map_file = feed_item.name.replace(" ","_")
        filepath = os.path.join("schemas",schema,map_file)
        writeToFile(content = data, filename = "mapping", folder = filepath , extension = ".xml", timestamp = False, overwrite = True)
        feed_item()
        
        
        
        