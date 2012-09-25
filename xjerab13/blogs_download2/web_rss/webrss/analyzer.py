import urllib2
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse, urljoin
import feedparser
from webrss.download import getDataFrom
from webrss.model.feed import Feed
from webrss.mapping import Mapper
try:
    import json
except:
    import simplejson as json

def getContentType(url):
    try : 
        r = urllib2.urlopen(url)
        return r.info()["Content-type"]
    except:
        return None
    


FEED_LINKS_ATTRIBUTES = (
    (('type', 'application/rss+xml'),),
    (('type', 'application/atom+xml'),),
    (('type', 'application/rss'),),
    (('type', 'application/atom'),),
    (('type', 'application/rdf+xml'),),
    (('type', 'application/rdf'),),
    (('type', 'text/rss+xml'),),
    (('type', 'text/atom+xml'),),
    (('type', 'text/rss'),),
    (('type', 'text/xml'),),
    (('type', 'text/atom'),),
    (('type', 'text/rdf+xml'),),
    (('type', 'text/rdf'),),
    (('rel', 'alternate'), ('type', 'text/xml')),
    (('rel', 'alternate'), ('type', 'application/xml')),
)



class PageAnalyzer(object):
    def __init__(self, url):
        self.url = url
        self.soup = None
        self.url_parse = None
        self.rss = []
        self.otherlinks = []
        self.parseUrl()
        
    def parseUrl(self):
        if not self.url.startswith("http"):
            self.url = "http://" + self.url
        
        self.url_parse = urlparse(self.url)
        print self.url_parse.netloc
        
        ctype = getContentType(self.url)
        ctype = ctype.split(";")[0]
        print ctype
        if (('type', ctype.lower()),) in FEED_LINKS_ATTRIBUTES:
            lnk = {}
            lnk["type"] = ctype
            lnk["text"] = ''
            lnk["url"] = self.url
            self.rss.append(lnk)
            print "is rss"
        else:
            self.soup = BeautifulSoup(urllib2.urlopen(self.url).read())
            print "is html"
        
        
    def getLinks(self):
        return self.rss
    
    def getOtherlinks(self):
        return self.otherlinks
        
        
    def findLinks(self, feed_links_attributes = FEED_LINKS_ATTRIBUTES):
        if self.soup is None:
            print "qq"
            return
        
        head = self.soup.find('head')
        for attrs in feed_links_attributes:
            for link in head.findAll('link', dict(attrs)):
                href = dict(link.attrs).get('href', '')
                if href: 
                    lnk = {}
                    lnk["type"] = link["type"]
                    lnk["text"] = link["title"]
                    pp = urlparse(link["href"])
                    if pp.netloc == '':
                        lnk["url"] = urljoin("http://" + self.url_parse.netloc, pp.path)
                    else:
                        lnk["url"] = link["href"]
                    self.rss.append(lnk)
    

    def findOtherLinks(self):
        if self.soup is None:
            print "qq"
            return
        
        alinks = self.soup.findAll("a")
        for link in alinks:
            #print link
            if not link.has_key("href"):
                continue
            pp = urlparse(link["href"])
            #print pp
            if pp.netloc == self.url_parse.netloc:
                ctype = getContentType(link["href"])
                if ctype:
                    ctype = ctype.split(";")[0]
                    #if ctype.endswith("xml"):
                    #print ctype
                    if (('type', ctype.lower()),) in FEED_LINKS_ATTRIBUTES:
                        lnk = {}
                        lnk["type"] = ctype
                        if link.text:
                            lnk["text"] = link.text
                        else:
                            lnk["text"] = "None"
                        lnk["url"] = link["href"]
                        self.otherlinks.append(lnk)
                        #yield json(lnk)
                        
            elif pp.netloc == '' and pp.path != '':
                newu = urljoin("http://" + self.url_parse.netloc, pp.path)
                ctype = getContentType(newu)
                if ctype:
                    ctype = ctype.split(";")[0]
                    #print ctype
                    if (('type', ctype.lower()),) in FEED_LINKS_ATTRIBUTES:
                        lnk = {}
                        lnk["type"] = ctype
                        lnk["text"] = link.text
                        lnk["url"] = newu
                        self.otherlinks.append(lnk)
                pass
        
   
class FeedAnalyzer(object):
    def __init__(self):
        self.feed = None
        self.item = None
        self.full_feed = None
        
    def analyze(self, feed_item, mapper):
        raw_feed = getDataFrom(feed_item.url, feed_item.logon, feed_item.password)
        self.full_feed = feedparser.parse(raw_feed)
        self.feed = self.full_feed.feed
        self.item = self.full_feed.entries[0]
        
        for key in mapper.funcs.keys():
            item = mapper.funcs[key]
            
            if item.text:
                item.text.found = True
                if item.text.functype == "buildin" and item.text.args != "":
                    item.text.found = False 
                    args = item.text.args.split(".")
                    if len(args) > 1:
                        val = getattr(self, args[0])
                        if val.has_key(args[1]):
                            item.text.found = True
                        
                            
                        
            for atr in item.attr:
                atr.found = True
                if atr.functype == "buildin" and atr.args != "":
                    atr.found = False
                    args = atr.args.split(".")
                    if len(args) > 1:
                        val = getattr(self, args[0])
                        if val.has_key(args[1]):
                            atr.found = True
                        
                            
                            
                
             
        
        

