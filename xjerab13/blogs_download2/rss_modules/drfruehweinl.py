from bdllib.baseclass.xmlgen import XmlGenerator
from time import sleep
import copy
from bdllib.pubmod.BeautifulSoup import BeautifulSoup
from bdllib.download import getDataFrom



class RSS_XmlGeneratorDrfruehwein(XmlGenerator):
    '''Class for minnning data from adress below'''
    myurl = "http://www.drfruehwein.de/epidemiologische-informationen/feed/rss.html"

    
    def __init__(self, folder, cache , guid ):
        XmlGenerator.__init__(self, folder, cache, guid)
        self.handle_url = "http://www.drfruehwein.de/epidemiologische-informationen/feed/rss.html"
        self.guid_prefix = "drfruehwein:"
    
    def update_feed(self, feed, url):
        '''function modify feed dict'''
        super(RSS_XmlGeneratorDrfruehwein,self).update_feed(feed, url)
        new_entries = []
        #print feed["entries"]
        
        timestamp = None
        
        if self.cache:
            timestamp = self.cache.loadFromCache(self.handle_url)

        
        for e in feed["entries"]:
            if timestamp >= e.date_parsed:
                    continue 
            sleep(1)
            page = getDataFrom(e["link"], self.username, self.password)
            if page is None:
                continue
            soup = BeautifulSoup(page)
            div = soup.find(id = 'page')
            strongs = div.findAll("strong")
            content = []
            for c in strongs:
                title = c.next
                text = c.next.next.next
                content.append([title,text])
                
     
            
            c = 0
            guid = e.id
            for item in content:
                title, text = item
                new_item = None
                new_item = copy.deepcopy(e)
                new_item["id"] = str(c)+":"+ guid
                new_item["title"] = title
                new_item["description"] = text
                new_entries.append(new_item)
                c +=1
        feed["entries"] = new_entries
        return
        