from bdllib.pubmod.BeautifulSoup import BeautifulSoup
import re
from htmlentitydefs import name2codepoint
import time
import logging

log = logging.getLogger("blog_download")
class PageParser(object):
    '''parsing HTML page from board.netdoktor.de'''
    
    def __init__(self, page):
        self._soup = None #beautifoulsoap
        self._excractor = None
        self.parseContent(page)
        self.url = None
       
    #parse page
    def parseContent(self, content):
        if content:
            self._soup = BeautifulSoup(content)
        
    
    def getSectionLenght(self):
        '''Return number of pages in certain section'''
        i = self._soup("div", id = "paginator")
        if i :
            return int(i[0]("a")[-1].next)
        else:
            return 1
    
    
        
    def getListOfItems(self):
        '''Return list of articles and their length.'''
        itemList = []
        divs = self._soup.findAll("div", "listing_item")
        for div in divs:
            
            item = {}
            if div.h2.a:
                item["url"] = div.h2.a["href"]
                #log.debug("Find link %s",item["url"])
            else:
                log.error("Article url not found.")
                continue
            s = div.find("span", "replies")
            coms = 0
            if s:
                try:
                    coms = int(filter(lambda x: x.isdigit(), s.a.text))
                except TypeError:
                    log.debug("for url %s cant found comments",item["url"])
                    pass
            item["comments"] = coms 
            itemList.append(item)
        return itemList

    
    def getEntriesList(self):
        '''Find all entries in article'''
        itemList = []
        header = self._soup.find("div", "listing_item_still")
        if header:
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
            title = " ".join(header.h1.next.split())
            content = " ".join(header.find("div", "listing_text").findAll(text = True))
            content = self.unescape(content)
            user_place = header.find("span", "listing_instr_detail text_meta")
            user = ""
            if user_place.a:
                user = user_place.a.next
            else:
                #ss = " ".join(user_place.findAll(text = True))
                #user = re.findall("Von\s*(\S*)\s*", str(ss))[0]
                user= user_place.find("span"," article_meta").next.next.split()[0]
                
            date = header.find("span", "listing_instr_detail text_meta").findAll("span")
            
            if date:
                date = date[-1].next[-8:]
                date = self.makeDate(date)
            else:
                log.error("error when date parsing, usin timestamp as date")
                date = timestamp
            
            itemList.append({"title":title, "text":content, "author":user, "pubDate":date, "timestamp":timestamp})
            
        else:
            log.error("error, main article not found")   
         
        comments = self._soup.findAll("div", "floatleft comment_entry_text")
        #print "found" + str(len(comments))
        cnt = 1
        for c in comments:
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
            content = " ".join(c.find("p", "comment_text").findAll(text = True))
            content = self.delControlChars(content)
            content = self.unescape(content)
            user = ""
            user_place = c.find("a", "article_meta")
                          
            if user_place:
                user = " ".join(user_place.next.split())
            else:
                user = " ".join(c.find("span","article_meta").next.next.split())
                
            date = c.find("span", "text_meta").findAll("span")
            
            if date:
                date = date[-1].next[-8:]
                date = self.makeDate(date)
            else:
                log.error("error when date parsing, usin timestamp as date")
                date = timestamp
            
            itemList.append({"title":title + " #" + str(cnt), "text":content, "author":user, "pubDate":date, "timestamp":timestamp})
            cnt += 1 
        
        return itemList
    
    
    def makeDate(self, date):
            '''Convert entry date to requested form'''
            date = date.split(".")
            if len(date) != 3:
                date = time.strftime("%d.%m.%y").split(".")
            date.reverse()
            date = date + [0]*(9-len(date))
            date = [int(x) for x in date]
            date = time.strftime("%Y-%m-%dT%H:%M:%S",date)
            return date
    
    
    def unescape(self, text): 
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
                    #print e
                    log.debug("html escape to unicode error %s", e)
                    pass
            else:
                # named entity
                try:
                    text = unichr(name2codepoint[text[1:-1]])
                except KeyError, e:
                    #print e
                    log.debug("name to unicode error %s", e)
                    pass
            return text # leave as is
        return re.sub("&#?\w+;", fixup, text)
        

    def delControlChars(self, text):
        mpa = dict.fromkeys(range(10)+[11,12]+range(14,32))
        text = text.translate(mpa)
        return text 
    
    
    



