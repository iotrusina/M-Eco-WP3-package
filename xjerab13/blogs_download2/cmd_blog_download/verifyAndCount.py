import glob
from xml.etree import ElementTree


itemscnt = 0
linkcnt = set([])
guidlist = []
dupitems = 0

def verify(file):
    global itemscnt
    global linkcnt
    global guidlist
    global dupitems
    try:
        f = open(file,"r")
        tree = ElementTree.parse(f)
        f.close()
    except Exception, e:
        print f.name
        print e
        if f:
            f.close()
        return
    
    for i in tree.getiterator("item"):
        itemscnt +=1
        for tag in i.getiterator():
            if tag.tag == "lang":
                text = " ".join(tag.text.split())
                if text != "de":
                    print "ERROR in da lang" + tag.text
            elif tag.tag == "guid":
                guid = " ".join(tag.text.split())
                if guid not in guidlist:
                    guidlist.append(guid)
                else:
                    dupitems +=1
                    #print "ERROR, duplicit guid in file " + file
                    #print guid
            elif tag.tag == "link":
                link = " ".join(tag.text.split())
                linkcnt.add(link)

def main():
    global itemscnt
    global linkcnt
    global guidlist
    global dupitem
    list = glob.glob("board_output_f1/*.xml")
    for f in list:
        verify(f)
    print "uniques link = " + str(len(linkcnt))
    print "all items    = " + str(itemscnt)
    print "dupliciites  = " + str(dupitems)
    
    


if __name__ == '__main__':
    main()
