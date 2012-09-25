import urllib2
from gzip import GzipFile
from StringIO import StringIO
import logging
from base64 import encodestring
from httplib import BadStatusLine

log = logging.getLogger("blog_download")
    
def getDataFrom(url, user, password, gzip=True):
    '''Download data from url. Can use siplme HTTP auth and gzip compression.
    
     Keyword arguments:
     url - target url for download
     user - username for http auth
     password - password for http auth
     gzip - enable/disable gzip data compression (default = Enable)
     
    '''
    page = None
    
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:5.0) Gecko/20100101 Firefox/5.0')
    req.add_header('Accept', '*/*')
    
    log.info("Downloading content from %s", url)
    
    if user and password:
        #if using http auth, need code data to base64  
        base64string = encodestring('%s:%s' % (user, password)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)
           
    if gzip:
        req.add_header("Accept-Encoding", "gzip")
        
    try:
        response = urllib2.urlopen(req)
        
        #print response.info()
    except urllib2.HTTPError, e :
        msg = 'The server couldn\'t fulfill the request.'
        if e.code == 401:
            msg += "\n      The page " + url +" request authentization, please fill username and password to file with urls"
        log.warning(msg)
        log.warning('Error code: %d', e.code)
    except urllib2.URLError, e:
        log.warning('Connection to %s failed. Reason: %s', url,e.reason)
    except BadStatusLine,e:
        #have no idea what triggers this exception
        #print "BadSTatusLIEN for url" + url
        log.critical("Bad Status Line For url %s", url)
    except IOError,e:
        log.critical("CRC error check %s", e)
        #page = getDataFrom(url, user, password, gzip = False) 
    else:
        if response.headers.get("content-encoding") == "gzip":
            page = GzipFile(fileobj=StringIO(response.read()), mode="r").read()
        else:
            page = response.read()
    return page
    





