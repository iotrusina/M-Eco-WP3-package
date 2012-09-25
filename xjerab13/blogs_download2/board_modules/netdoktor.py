from urlparse import urljoin
from xml.dom.minidom import Document
import logging
from bdllib.download import getDataFrom
from bdllib.cache import CacheHandler
from bdllib.boardparsers.netdoktorparser import PageParser
from bdllib.shared_func import writeToFile




boards = [
"Allergie",
"Alter-Pflege",
"Alzheimer-Demenz",
"Asthma",
"Augen",
"Brustkrebs",
"Diabetes",
"Ernaehrung-Diaeten",
"Geschlechtskrankheiten",
"Gesundheit-Medizin",
"Grippe-Erkaeltung",
"Hals-Nasen-Ohren",
"Haut-Haare",
"Herz-Kreislauf",
"Impfungen",
"Kinderkrankheiten",
"Kopfschmerzen-Migraene",
"Krebs",
"Magen-Darm-Verdauung",
"Multiple-Sklerose-MS",
"Muskeln-Knochen-Gelenke",
"Nieren-Harnwege",
"Potenz-Erektionsstoerungen",
"Psyche",
"Rueckenschmerzen",
"Schilddruese",
"Schlafstoerungen",
"Schwangerschaft-Baby",
"Sexualitaet-Verhuetung",
"Sucht",
"Wechseljahre",
"Zaehne"]

sections = [
"Fragen",
"Grundlagenwissen",
"Forum",
"Tipps",
"Tags",
"Artikelvorschlaege",
]


log = logging.getLogger("blog_download")

class Board_NetDoktorParser(object):
    '''Module for text minning from board.netdoktor.de'''
    def __init__(self, folder):
        self._url = "http://board.netdoktor.de"
        self.pageCache = CacheHandler()
        self.contentCache = CacheHandler()
        self.dataToStore = [] #list of items to store
        self.board = None
        self.section = None
        self.outputFolder = folder

    
    #add some stacionary data to all items in list
    def addItemToFinalList(self, name, data):
        for i in range(len(self.dataToStore)):
            self.dataToStore[i][name] = data
        pass
    
    
    def updateContent(self, url):
        '''if new entries in article found, they are processing and add to list to save'''
        #print url[25:]
        #pbar(url[25:])
        #print ".",
        #log.debug("UPDATING data from - %s",url)
        page = getDataFrom(url, None, None)
        
        if page == None:
            return False
        
        pageParser = PageParser(page)
        notCached = pageParser.getEntriesList()
        #print notCached
        eToStore = self.pageCache.cacheAndReturnNew(url, notCached)
        
        for i in range(len(eToStore)):
            eToStore[i]["link"] = url
        #print "adding" + str(len(eToStore))  
        log.debug("ADD %d new entries", len(eToStore))
        
        self.dataToStore.extend(eToStore)
               
        return True
    
        
    
    
    def processData(self, itemList):
        '''proces links to articles in forum section page, if change detect, update appeared'''
        #print itemList
        for item in itemList:
            cached = self.pageCache.getEntriesLen(item["url"])
            loaded = item["comments"] + 1
            #new comments in article detected
            if cached < loaded:
                #print "ecpect " + str(loaded-(cached))
                #print "need update for " + item["url"]
                msg = "need update for %s - %d new ent" %(item["url"],loaded - cached)
                log.debug(msg)
                if self.updateContent(item["url"]):
                    self.pageCache.setEntriesLen(item["url"], loaded)
            else:
                log.debug("no new entries for %s", item["url"])
                pass
    
        pass
    
    
    def processSection(self, bsection):
        '''process all pages in forum section'''
        actualPage = 1
        sectionLenght = None
        url = urljoin(self._url,bsection)
        while(True):
            try:
                urll = url + "/" + str(actualPage) 
                #urll = url + "/" + str(151)
                page = getDataFrom(urll, None, None)
    
                #print "PS for " + url
                if page is None and sectionLenght is None:
                    log.debug("none data, return")
                    return
                elif page is None and sectionLenght != None:
                    log.debug("none data, continue")
                    continue
                
                pageParser = PageParser(page)
                if not sectionLenght:
                    #get max page in section
                    sectionLenght = pageParser.getSectionLenght()
                    #print "sectionLenght is" + str(sectionLenght)
                    log.debug("sectionLenght is %s" , str(sectionLenght)) 
                    
                itemList = pageParser.getListOfItems()
                
                
                self.processData(itemList)
                #add stacionary data
                self.addItemToFinalList("source", "http://board.netdoktor.de/")
                self.addItemToFinalList("section", "netdoktor")
                self.addItemToFinalList("lang", "de")
                #SAVE!!!
                self.createXmlandWrite(name = bsection.replace("/","_"))
            except Exception,e:
                log.critical("%s",e)
                log.exception("Some exception in process section")
                
            if actualPage >= sectionLenght:
                return
            actualPage += 1
    
    
    
    def processBoard(self, board):
        '''func generate url for board and their sections'''
        self.pageCache.createPersistenCache("netdoktor_"+board)
        #self.pageCache.createMemoryCache()
        for section in sections:
            #print board + " " + section
            self.processSection(board+"/"+section)
        self.pageCache.closeCache()
    
    
    def work(self):
        log.debug("Crawling netdoctor.de")
        self.contentCache.createDbCache("guidcache", ext = ".db")
        for board in boards:
            self.processBoard(board)
        self.contentCache.closeCache() 
       
            
            
    def createXmlandWrite(self, name):
        '''From parsed data, create final xml document'''
        if not self.dataToStore:
            return 
        
        doc = Document()
        results = doc.createElement("results")
        doc.appendChild(results)
        #walk over list of data
        for a in self.dataToStore:
            item = doc.createElement("item")
            for k, d in a.items():
                tag = doc.createElement(k)
                
                if k == "author":
                    tag2 = doc.createElement("name")
                    data = doc.createTextNode(d)
                    tag2.appendChild(data)
                    tag.appendChild(tag2)
                elif k == "text":
                    mpa = dict.fromkeys(range(10)+[11,12]+range(14,32))
                    d = d.translate(mpa)
                    data = doc.createTextNode(" ".join(d.split()))
                    tag.appendChild(data)
                else:
                    data = doc.createTextNode(" ".join(d.split()))
                    tag.appendChild(data)
                item.appendChild(tag)
            results.appendChild(item)
        
        
        writeToFile(doc.toprettyxml(indent="    ", encoding = "UTF-8"), 
                    name, 
                    self.outputFolder, 
                    extension=".xml", 
                    timestamp=True
                    )
        
        self.dataToStore = []
        
            
          
    
    
    

    
