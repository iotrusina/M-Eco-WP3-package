import urllib2
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse, urljoin
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
        self.soup = BeautifulSoup(urllib2.urlopen(self.url).read())
        
        
    def getLinks(self):
        return self.rss
    
    def getOtherlinks(self):
        return self.otherlinks
        
        
    def findLinks(self, yielding = False):
        rss = self.soup.findAll("link",{"type":"application/rss+xml"})
        atom = self.soup.findAll("link",{"type":"application/atom+xml"})
        
        for i in rss:
            lnk = {}
            lnk["type"] = i["type"]
        
            lnk["text"] = i["title"]
            
            pp = urlparse(i["href"])
            if pp.netloc == '':
                lnk["url"] = urljoin("http://"+self.url_parse.netloc,pp.path)
            else:
                lnk["url"] = i["href"]
            self.rss.append(lnk)
            #yield json(lnk)
            
        for i in atom:
            lnk = {}
            lnk["type"] = i["type"]
        
            lnk["text"] = i["title"]
            lnk["url"] = i["href"]
            self.rss.append(lnk)
            #yield json(lnk)
        
    

    def findOtherLinks(self):
        alinks = self.soup.findAll("a")
        for link in alinks:
            if not "href" in link._getAttrMap():
                continue
            pp = urlparse(link["href"])
            #print pp
            if pp.netloc == self.url_parse.netloc:
                ctype = getContentType(link["href"])
                if ctype:
                    ctype = ctype.split(";")[0]
                    if ctype.endswith("xml"):
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
                newu = urljoin("http://"+self.url_parse.netloc,pp.path)
                ctype = getContentType(newu)
                if ctype:
                    ctype = ctype.split(";")[0]
                    if ctype.endswith("xml"):
                        lnk = {}
                        lnk["type"] = ctype
                        lnk["text"] = link.text
                        lnk["url"] = newu
                        self.otherlinks.append(lnk)
                pass
        
   
   
