import os, sys
import time
import logging
from bdllib.pubmod.BeautifulSoup import name2codepoint
import re

log = logging.getLogger("blog_download")


'''Some shared universal funcions'''

def makePath(path):
    '''Creating absolute path based on program position in filesystem.'''
    if os.path.isabs(path):
        return path
    else:
        return os.path.join(sys.path[0], path)
    
def createFolderStruc(folder):
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    
def writeToFile(content, filename, folder , extension = "", timestamp = True):
    '''Write content data to file.
    
    Keyword arguments:
    timestamp - append filestam to filename (default = Enabled)
    
    
    '''
    if timestamp:
        filename += time.strftime("%Y%m%dT%H%M%S")
        
    if not extension.startswith("."):
        extension = "." + extension
    
    createFolderStruc(folder)       
    path = os.path.join(folder, filename)
    g = open(path, "wt") 
    g.write(content)
    g.close()
    cnt = 1
    newname = ""
    if os.path.exists(path + extension):
        while os.path.exists(path + "." + str(cnt) + extension):
            cnt += 1
        newname = os.path.splitext(path)[0] + "." + str(cnt) + extension
    else:
        newname = os.path.splitext(path)[0] + extension
    os.rename(path, newname)
    msg = "Data saved to: %s", newname
    log.info(msg)


def toUnicode(text,decoding="utf-8"):
    '''Convert text to unicode'''
    if isinstance(text, str):
        return unicode(text, decoding)
    elif isinstance(text, unicode):
        return text
    else:
        return text    
   
def fromUnicode(text,encoding = "utf-8"):
    '''Convert text from unicode to str'''
    if isinstance(text, str):
        return text
    elif isinstance(text, unicode):
        return text.encode("utf-8")
    else:
        return text
    
def unescape(text):
        '''Convert HTML escape chars to regular chars'''
     
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
                    log.error("html escape to unicode error %s", e)
                    pass
            else:
                # named entity
                try:
                    text = unichr(name2codepoint[text[1:-1]])
                except KeyError, e:
                    #print e
                    log.error("name to unicode error %s", e)
                    pass
            return text # leave as is
        return re.sub("&#?\w+;", fixup, text)
    
def pbar(string):
    #print '\r'+string+" "*(80-len(string))
    sys.stdout.write(string+" "*(79-len(string))+'\r')

    
