import urllib2
from gzip import GzipFile
from StringIO import StringIO
import logging

    
def getDataFrom(url):
    #opener = urllib2.build_opener(_GZipProcessor)
    #urllib2.install_opener(opener)
    
    page = None
    req = urllib2.Request(url)
    req.add_header("Accept-Encoding", "gzip")
        
    try:
        response = urllib2.urlopen(req)
        
        #print response.info()
    except urllib2.HTTPError,e :
        msg = 'The server couldn\'t fulfill the request.'
        if e.code == 401:
            msg += "\n      The page " + url +" request authentization, please fill username and password to file with urls"
        logging.warning(msg)
        logging.warning('Error code: %d', e.code)
    except urllib2.URLError, e:
        logging.warning('Connection to %s failed. Reason: %s', url,e.reason)
    else:
        if response.headers.get("content-encoding") == "gzip":
            page = GzipFile(fileobj=StringIO(response.read()), mode="r").read()
        else:
            page = response.read()
    return page
    


class _GZipProcessor(urllib2.BaseHandler):
    def http_request(self, req):
        req.add_header("Accept-Encoding", "gzip")
        return req
    https_request = http_request
    
    def http_response(self, req, resp):
        if resp.headers.get("content-encoding") == "gzip":
            #print "weeeeee gzip"
            gz = GzipFile(
                        fileobj=StringIO(resp.read()),
                        mode="r"
                      )
            gzip_resp = resp
            #print gz, gzip_resp.headers, gzip_resp.url, gzip_resp.code
            resp = urllib2.addinfourl(gz, gzip_resp.headers, gzip_resp.url, gzip_resp.code)
            print gzip_resp.msg
            resp.msg = gzip_resp.msg
        return resp
    https_response = http_response


