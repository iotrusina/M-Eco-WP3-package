import re
from htmlentitydefs import name2codepoint
from hashlib import sha224
from bdllib.baseclass.xmlgen import XmlGenerator

class RSS_XmlGeneratorRsoeEdis(XmlGenerator):
    '''Class for minnning data from adress below'''
    def __init__(self, folder, cache , guid ):
        XmlGenerator.__init__(self, folder, cache, guid)
        self.handle_url = "http://feeds.feedburner.com/RsoeEdis-Ebhwm"
        self.guid_prefix = "rsoeedis:"
  
        
    def update_feed(self, feed, url):
        super(RSS_XmlGeneratorRsoeEdis,self).update_feed(feed, url)
        feed["feed"]["language"] = "en"
    
    def tag_guid(self):
        path = ["entries" ,"_C_", "content"]
        func = lambda x: self.guid_prefix + str(sha224(self.text_writer(x).encode("utf-8")).hexdigest())
        req = True
        return path,func, req
    
       
    def tag_georss(self):
        path = ["entries","_C_","georss_point"]
        func = lambda x: dict(zip(["lat","lon"],x.split()))
        req = False
        return path, func, req

    def tag_text(self):
        path = ["entries" ,"_C_", "content"]
        func = self.text_writer
        req = True
        return path, func, req
    
    def text_writer(self,data):
        text = ""
        for d in data:
            output  = re.compile('<code>(.*?)</code>', re.DOTALL |  re.IGNORECASE).findall(d.value)
            for t in output:
                text +=self.unescape(t.replace("&amp;", "&"))
  
        return text
    
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