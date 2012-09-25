import string
from webrss.model.feed import Feed
from webrss.mapping import Mapper
import pprint
from webrss.shared_func import writeToFile
import os

imports = ["re","hashlib","urlparse","copy", "time"]
import re
importsf = {"webrss.downloaders":"BaseDownloader",
            "webrss.download":"getDataFrom",
            "webrss.shared_func":"writeToFile",
            "xml.etree":"ElementTree",
            "BeautifulSoup":"BeautifulSoup",
            
            }
class CodeGenerator():
    
    @classmethod
    def getClassName(self, feed_item):
        rx = re.compile('[^\d\w]')
        return rx.sub('_',str("ID_" + str(feed_item.id) + "_"+ feed_item.output_scheme + "_" + feed_item.map_rules))

    def begin(self, tab=" "):
        self.code_imports = []
        self.code_head = []
        self.code = []
        self.tab = tab
        self.level = 0 

    def end(self):
        return string.join(self.code_imports, "\n") + "\n\n" + string.join(self.code_head, "\n") + "\n\n" + string.join(self.code, "\n")

    def writeHead(self,string):
        self.code_head.append(self.tab * self.level + string)
        
    def writeImport(self, string):
        self.code_imports.append(self.tab * self.level + string)
    
    def writeLine(self, string):
        self.code.append(self.tab * self.level + string)
        
    def writeBlock(self, block):
        self.code.extend([self.tab * self.level + x for x in block.strip().split("\n")])
        
    def writeFunc(self, fname, code, attr = ["self"]):
        
        if not code:
            code = 'return ""'
        if not "self" in attr:
            attr.insert(0,"self")
        self.writeLine("def " + fname+"("+", ".join(attr)+"):")
        self.indent()
        self.writeBlock(code)
        self.writeLine("")
        self.dedent()
        

    def indent(self):
        self.level = self.level + 1

    def dedent(self):
        if self.level == 0:
            raise SyntaxError, "internal error in code generator"
        self.level = self.level - 1
    

    def writeImports(self):
        for i in imports:
            self.writeImport("import " + i)
        for k,d in importsf.items():
            self.writeImport("from " + k + " import " +d)
    
    
    def generateCode(self, feed):
        
        #feed = Feed.findById(feed_id)
            
        classname = CodeGenerator.getClassName(feed)
        mapper = Mapper(feed)
        mapper.loadMappingAsDict()
        self.begin(tab="    ")
        self.writeImports()
        self.writeHead("class Downloader(BaseDownloader):")
        self.indent()

        if mapper.func_update:
            self.writeFunc("update_feed",mapper.func_update, ["self","raw_feed"])
        
        for tag,body in mapper.funcs.items():
            if body["text"]:
                if body["text"]["functype"] == "userfunc":
                    fname = ("get_"+tag+"_text").replace("/","_")
                    self.writeFunc(fname, body["text"]["func_name"])
                    body["text"]["func_name"] = fname
                
            for a in body["attr"]:
                if a["functype"] == "userfunc":
                    fname = ("get_"+tag+"_attr_"+a["name"]).replace("/","_")
                    self.writeFunc(fname, a["func_name"])
                    a["func_name"] = fname
        
        pp = pprint.PrettyPrinter(indent = 4)
        self.writeHead("prules = " + pp.pformat(mapper.funcs))
        writeToFile(content = self.end(),
                    filename = classname, 
                    folder = os.path.join("webrss","downloaders"), 
                    extension = ".py", 
                    timestamp = False,
                    overwrite = True)
        