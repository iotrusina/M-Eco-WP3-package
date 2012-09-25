from urlparse import urljoin
from download import getDataFrom
from netdoktorparser import PageParser
from cache import SimpleCache
from xml.dom.minidom import Document
import logging
import time



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
"Grundlagenwissen",
"Forum",
"Tipps",
"Tags",
"Artikelvorschlaege",
"Fragen"]


class NetDoktorHandler(object):
    def __init__(self):
        self._url = "http://board.netdoktor.de"
        self._cache = SimpleCache()
        self.dataToStore = []
        self.board = None
        self.section = None

    

    def addItemToFinalList(self, name, data):
        for i in range(len(self.dataToStore)):
            self.dataToStore[i][name] = data
        pass
    
    
    def updateContent(self, url):
        #print "   updating from " + url
        logging.debug("UPDATING data from - %s",url)
        page = getDataFrom(url)
        
        if page == None:
            
            return
        
        pageParser = PageParser(page)
        notCached = pageParser.getEntriesList()
        #print notCached
        eToStore = self._cache.cache(url, notCached)
        
        for i in range(len(eToStore)):
            eToStore[i]["link"] = url
            
        logging.debug("ADD %d new entries", len(eToStore))
        
        self.dataToStore.extend(eToStore)
               
        pass
    
        
    
    
    def processData(self, itemList):
        #print itemList
        for item in itemList:
            x = self._cache.isCached(item)
            if not x:
                self.updateContent(item["url"])
        
    
        pass
    
    
    def processSection(self, url):
        actualPage = 1
        sectionLenght = None
        while(True):
            urll = url + "/" + str(actualPage) 
            page = getDataFrom(urll)

            #print "PS for " + urll
            if page is None and sectionLenght is None:
                print "none data, return"
                return
            elif page is None and sectionLenght != None:
                print "none data, continue"
                continue
            
            pageParser = PageParser(page)
            if not sectionLenght:
                sectionLenght = pageParser.getSectionLenght()
                #print "sectionLenght is" + str(sectionLenght) 
                
            itemList = pageParser.getListOfItems()
            
            self.processData(itemList)
            self.addItemToFinalList("source", urll)
            self.addItemToFinalList("section", "netdoktor")
            self.addItemToFinalList("lang", "de")
            self.storeToFile(actualPage)
            if actualPage == sectionLenght:
                return
            actualPage += 1
    
    
    
    def run(self):
        
        self.setLogging("debug", "log.log")
        
        logging.info("Starting app")
        for board in boards:
            self.board = board
            for sec in sections:
                self.section = sec
                url = urljoin(self._url, board + "/" + sec)
                self.processSection(url)
        logging.info("LE END")        
            
            
    def storeToFile(self, suffix = ""):
        if not self.dataToStore:
            return 
        
        doc = Document()
        results = doc.createElement("results")
        doc.appendChild(results)
        for a in self.dataToStore:
            item = doc.createElement("item")
            for k, d in a.items():
                tag = doc.createElement(k)
                if k == "author":
                    tag2 = doc.createElement("name")
                    data = doc.createTextNode(d)
                    tag2.appendChild(data)
                    tag.appendChild(tag2)
                else:
                    data = doc.createTextNode(" ".join(d.split()))
                    tag.appendChild(data)
                item.appendChild(tag)
            results.appendChild(item)
            
        
        timestamp = time.strftime("%H%M%S_")
        f = open("output/" + timestamp + self.board + "_" + self.section + "_" + str(suffix) + ".xml", "w")
        f.write(doc.toprettyxml(indent = "    ", encoding = "utf-8"))
        f.close()
        self.dataToStore = []
        
            
            
            
                
    def setLogging(self, level, filename):
        LEVELS = { 'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'critical':logging.CRITICAL,
        }
        loglevel = LEVELS.get(level, logging.NOTSET)
    
        logging.basicConfig(filename=filename,level=loglevel,
                        format='%(levelname)s: (%(asctime)-15s) - %(message)s'
                        )

    



if __name__ == '__main__':
    try:
        h = NetDoktorHandler()
        h.run()
    except Exception ,e:
        logging.error("ouha error %s",e)
        
    
    
    

    
