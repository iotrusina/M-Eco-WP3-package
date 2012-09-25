#!usr/bin/env python

import sys
import hashlib
#reload(sys)
#sys.setdefaultencoding('utf-8')
import db_downloader
from autoapi.autoapi import *
import timer
from rytools import control_chars


SOURCE_ID = 8793 # URLENTITY source
GUID_PREFIX = "urlentity"



def download_and_insert(url, pubdate, pubtime):
    try:
        data = db_downloader.download_url(url)
    except Exception, e:
        print e
        return None
    if not data.get('text'):
        print 'db_url-stahovak: no text'
        return
    dbdoc = Documents()
    dbdoc.set_pubDate(pubdate)
    dbdoc.set_pubTime(pubtime)
    dbdoc.set_text( control_chars.remove(data['text']) )
    dbdoc.set_title( control_chars.remove(data.get('title', '')) )
    dbdoc.set_source_id(SOURCE_ID)
    dbdoc.set_language(u'en')
    dbdoc.set_timestamp(timer.timestamp())
    dbdoc.set_link( url )
    dbdoc.set_html_description( control_chars.remove(data.get('description', '')) )
    dbdoc.set_html_keywords( control_chars.remove(data.get('keywords', '')) )
    dbdoc.set_guid( GUID_PREFIX + ":" + hashlib.sha224(url).hexdigest() )
    ok, id = dbdoc.insert()
    return id





if __name__ == '__main__':
    """Download for each line in form 'url\tpubdate\tpubtime'"""
    for line in sys.stdin:
        line = line.strip()
        if len(line) == 0:
            continue
        url, pubdate, pubtime = line.split("\t")
        download_and_insert(line, pubdate, pubtime)
        



