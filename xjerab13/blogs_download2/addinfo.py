import glob
from xml.etree import ElementTree
from xml.dom import minidom
import re
import time

filelist = glob.glob("/mnt/data/nlp/projects/blogs_download2/netdoktor/output/*.xml")
output = "/mnt/data/nlp/projects/blogs_download2/board_output/"

#filelist =  glob.glob("c:\\workspace\\python\\blog_downloader\\src\\board_output\\*.xml")
#output = "c:\\workspace\\python\\blog_downloader\\src\\board_output\\"


def main():
    for file in filelist:
        f = open(file,"r")
        try:
            tree = ElementTree.parse(f)
        except Exception,e:
            print f.name
            print e
                    
            continue
        name = f.name
        name = name.split("/")[-1]
#        name = name.split("_")
#        date = time.strftime("%y%m%dT%H%M%S")
#        boadr = name[1]
#        section = name[2]
#        rest = name[3]
        #name = boadr+"_"+section+"_"+date+"."+rest
        
        #print "#"
        f.close() 
        
        for node in tree.iter('guid'):
            #print node.text
            
            t = node.text
            m = re.search("\S", t)
            x = m.start()
            t = t[:x] + "netdoktor:" + t[x:]
            node.text = t
        f = open(output+name,"w")
        f.write(prettify(tree.getroot()))
        f.close()
       


def update(tree):
    for node in tree.iter('guid'):
            print node.text
            t = node.text
            t = "netdoktor:" + t
            node.text = t
        #print prettify(tree.getroot())
     
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem)
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="", newl="", encoding="utf-8")

if __name__ == '__main__':
    main()
    