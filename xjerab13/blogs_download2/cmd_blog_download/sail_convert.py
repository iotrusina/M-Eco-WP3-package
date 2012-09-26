from xml.etree import ElementTree
import time
from xml.dom.minidom import Document
import glob
from bdllib.shared_func import writeToFile, toUnicode
import os
from hashlib import sha256

class SailConvertor:
    def __init__(self):
        self.inlist = []
        self.guidlist = []
        
    def convertFile(self, filepath):
        outputdict = {}
        
        f = open(filepath, 'rt')
        try:
            tree = ElementTree.parse(f)
        except:
            print "    EROOR"
            f.close()
            return
        f.close()
        
        
        #print self.text_creator(tree)
        outputdict["lang"] = tree.find("./meta/language").text[:2] 
        #pubdate = tree.find("./meta/absolutetime").text
        a = tree.find("./meta/indexingDate").text
        pbdate = a[:4] + "-" + a[4:6] + "-" + a[6:]
        pubdate =  pbdate + "T" +tree.find("./meta/indexingTime").text
        #outputdict["pubDate"] = time.strftime("%Y-%m-%dT%H:%M:%S",time.localtime(float(pubdate)))
        outputdict["pubDate"] = pubdate
        outputdict["text"] = self.text_creator(tree)
        outputdict["title"] = tree.find("./meta/mediaName").text 
        outputdict["section"] = "sail-labs"
        outputdict["source"] = "ftp.sail-labs.com"
        outputdict["link"] = "file:"+ os.path.split(filepath)[1]
        outputdict["author"] = ""
        outputdict["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        outputdict["guid"] = "TV:" + tree.getroot().attrib["id"].split(",")[0]
        
        if outputdict["guid"].encode("utf-8") in self.guidlist:
            print "already in"
            return
        
        if sha256(outputdict["text"].encode("utf-8")).hexdigest() in self.inlist:
            print "fup found"
            return
        
        self.createXmlandWrite([outputdict], os.path.split(filepath)[1])
        
        pass
    
    def text_creator(self, tree):
        text = ""
        for node in tree.getiterator('word'):
            if node.text is not None:
                text += "".join([a+" " for a in node.text.split()])
        
        text = text.replace(" .",".")
        text = " ".join(text.split())
        return text
    
    def createXmlandWrite(self, dataToStore, filename):
        if not dataToStore:
            return 
        
        doc = Document()
        results = doc.createElement("results")
        doc.appendChild(results)
        for a in dataToStore:
            item = doc.createElement("item")
            for k, d in a.items():
                tag = doc.createElement(k)
                
                if k == "author":
                    tag2 = doc.createElement("name")
                    data = doc.createTextNode(d)
                    tag2.appendChild(data)
                    tag.appendChild(tag2)
                else:
                    data = doc.createTextNode(toUnicode(d))

                    tag.appendChild(data)
                item.appendChild(tag)
            results.appendChild(item)
        
        qwe = doc.toprettyxml(indent="    ", encoding = "UTF-8")
       

        writeToFile(qwe, 
                    "scf_"+filename, 
                    "/mnt/minerva1/nlp/projects/spinn3r/solr_data/xjerab13",
			#"/mnt/minerva1/nlp/projects/blogs_download2/sail_data_out",
			#"e:\\tmp\\tmp\\conv", 
                    extension=".xml", 
                    timestamp=True
                    )
    


if __name__ == '__main__':
    qq = SailConvertor()
    aa = None
    f = open("all.txt","r")
    aa = f.read()
    print aa[:20]
    f.close()

    aa = aa.split('\n')
    print aa[0]
    for a in aa:
        d = a.split(' ')
        if len(d) > 1:
            qq.inlist.append(d[1])
            qq.guidlist.append(d[0])
    
    print "loaded hashes ", len(qq.inlist) 
    
    #or f in glob.glob(u"e:\\tmp\\tmp\\orig\\*.xml"):
    for f in glob.glob(u"./sail_data/*.xml"):
        print "converting ", f
        qq.convertFile(f)
        
    
    
