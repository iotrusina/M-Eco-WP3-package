import cherrypy
from webrss.model.feed import Feed
from mako.lookup import TemplateLookup
from xml.etree import ElementTree
import feedparser
from xml.etree.ElementTree import iterparse
from webrss.mapping import Mapper
from webrss.analyzer import FeedAnalyzer
import os
from webrss.shared_func import writeToFile
from webrss.codegenerator import CodeGenerator
import py_compile
from py_compile import PyCompileError
import cgi
import re

lookup = TemplateLookup(directories = ['interface'])

class DBView(object):
    
    @cherrypy.expose
    def index(self):
        items = Feed.findAll()
        tmpl = lookup.get_template("database.html")
        return tmpl.render(items = items, pgname="db")
        
    @cherrypy.expose
    def edit_feed(self, item_id):
        item = Feed.findById(item_id)
        tmpl = lookup.get_template("edit_feed.html")
        return tmpl.render(item = item, pgname="edit_feed")
    
    @cherrypy.expose
    def edit_feed_map(self, item_id, schema=None):
        item = Feed.findById(item_id)
        
        if schema:
            item.output_scheme = schema
            item.map_rules = ''
            
        m = Mapper(item)
        m.loadScheme()
        m.loadMapping()
        
        f = None
        if item.output_scheme:
            f = FeedAnalyzer()
            f.analyze(item, m)
            
        
        tmpl = lookup.get_template("edit_feed_map.html")
        return tmpl.render(item = item, mapper = m,pgname="edit_feed_map", flz = f)
    
    
        
    @cherrypy.expose    
    def savefeed(self, item_id, schema, data, testdownload = "false"):
        feed_item = Feed.findById(item_id)
        map_file = str(feed_item.id) + "_" + feed_item.name
        rx = re.compile('[^\d\w]')
        map_file = rx.sub("_", map_file)
        filepath = os.path.join("schemas",schema, map_file)
        try:
            yield "saving xml file..."
            writeToFile(content = data, filename = "mapping", folder = filepath , extension = ".xml", timestamp = False, overwrite = True)
            yield "OK"+ "<br/>"
            feed_item.output_scheme = schema
            feed_item.map_rules = map_file
            yield "generating python code..."
            CodeGenerator().generateCode(feed_item)
            yield "OK"+ "<br/>"
            classname = CodeGenerator.getClassName(feed_item)
            #folder = os.path.join("webrss","downloaders")
            yield "compile test..."
            py_compile.compile(os.path.join(os.path.join("webrss","downloaders"),classname+".py"), doraise = True)
            yield "OK"+ "<br/>"
            feed_item.save()
            if testdownload == "true":
                yield "Testing download..."
                feed_item.cache_data = feed_item.cache_data - (8*24*60*60)
                m = __import__(classname)
                m = reload(m)
                out = m.Downloader().parseFeed(feed_item)
                p = re.compile("^([\s]+)", re.MULTILINE)
    
                yield "OK"+ "<br/>"
                out =  cgi.escape(out)
                out = p.sub(lambda x: (x.end()-x.start())*"&nbsp&nbsp",out)
                yield out.replace("\n","<br>")
        except PyCompileError, e:
            yield "Error in compiling:"+ "<br/>"
            yield e.exc_type_name + "<br/>"
            yield e.exc_value[0] + " on line, with text: " + e.exc_value[1][3]+ "<br/>"
        except Exception, e:
            #yield "Error in compiling:"+ "<br/>"
            #yield e.exc_type_name + "<br/>"
            #yield e.exc_value[0] + " on line, with text: " + e.exc_value[1][3]+ "<br/>"
            yield str(e) + "<br/>"
        
    savefeed._cp_config = {'response.stream': True}
        
        

    @cherrypy.expose
    def add(self, type, name, url):
        a = {"id":None,
             "type": type,
             "name": name,
             "url": url,
             "update_time":None,
             "last_update":None,
             "cache_file":None,
             "cache_type":None,
             "output_scheme":None,
             "map_rules":None,
             "logon":None,
             "password":None
                  }
        q = Feed(**a)
        q.save()
        
class struct():
    pass