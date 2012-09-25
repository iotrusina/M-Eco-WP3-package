#!usr/bin/env python
# 
# Copyright 2010 Vojtech Rylko
#

"""Ad-Hoc module for downloading items from feed with memory via db."""

__author__ = "xrylko00@stud.fit.vutbr.cz"

import feedparser
import logging
import datetime
import urllib2
import socket
import sys
import hashlib
import lxml
import lxml.html
from BeautifulSoup import UnicodeDammit

import bte

# because lxml problems with encoding
reload(sys)
sys.setdefaultencoding("utf-8")

logger = logging.getLogger("db_stahovak.db_downloader")
logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.ERROR)

def download_url(url):
    """Ad-hoc.
    Download url and gain informations about page.

    Catch some obvious exceptions - http and socket related.

    @return: empty dict or with informations (html/head):
    - raw  - before bte
    - text - after bte
    - keywords
    - discription 
    - author
    - title
    """
    result = {}
    try: 
        conn = urllib2.urlopen(url)
        webfile = conn.read()
    except Exception, e: 
        logger.info("Cannot download URL:%s\t%s", url, e)
    else:
        if not webfile:
            return result
        converted = UnicodeDammit(webfile) #, isHTML=True)
        if not converted.unicode:
            logger.info("UnicodeDammit failed to detect encoding, tried [%s]", \
                 ', '.join(converted.triedEncodings))
            return result
        logger.debug("UnicodeDammit: originalEncoding:%s, triedEncodings:%s",
                 converted.originalEncoding, ', '.join(converted.triedEncodings))
        result['raw'] = converted.unicode
        result['text'] = bte.html2text(converted.unicode)
        root = None
        try:
            root = lxml.html.fromstring(webfile)
        except lxml.etree.ParserError, e:
            logger.info("Can not parse URL:%s\t%s", url, e)
            return dict()
        find = {'description' : "./head/meta[@name=\"description\"]/@content",
                'keywords' : "./head/meta[@name=\"keywords\"]/@content",
                'title' : "./head/title/text()",
                'lang'  : "./html[@name=\"lang\"]"}
        for key, value in find.iteritems():
            try : 
                result[key] = root.xpath(value)[0]
            except UnicodeDecodeError, e: 
                logger.info("UnicodeDecodeError\t%s", e)
            except IndexError: continue
    return result


def date2ISO(date):
    """Ad-Hoc. Convert datetime to ISO datetime.
    
    @return: unicode string"""
    if date == "": return date
    return unicode(datetime.datetime(*date[0:7]).isoformat())


def download(url, etag = None, modified = None):
    """Download entries from feed's `url`. 
    """
    result = {'error'       : False,
              'error_msg'   : 'No error detected',
              'etag'        : None,
              'modified'    : None,
              'status'      : None,
              'url'         : url,
              'feed_info'   : {},
              'items_count' : 0,
              'items'       : []}
    logger.info("Parse URL:%s\tETAG:%s\tMODIFIED:%s", url, etag, modified)
    try:
        d = feedparser.parse(url, etag=etag, modified=modified)
    except UnicodeDecodeError, e:
        result['error']     = True
        result['error_msg'] = "Feedparser.parse\t%s" % e
        return result
    try : status=d.status
    except AttributeError: 
        result['error']     = True
        result['error_msg'] = 'AttributeError - no STATUS set.'
        if d.bozo:
            bozo_info = d.bozo_exception
            result['error_msg'] += "\tbozo_exception:%s" % bozo_info
            return result
    else:
        result['status'] = status
    if len(d.entries) == 0:
        return result
    etag     = d.get('etag')
    modified = d.get('modified')
    result['etag']      = etag
    result['modified']  = modified
    # feed info - just copy
    copy = ['title', 'encoding', 'link', 'description', 'date', 'date_parsed']
    for c in copy:
        result['feed_info'][c] = d.feed.__dict__.get(c, "")
    
    # items
    for i in d.entries:
        # prepare `text`
        item = {'guid'      : None,
                'text'      : None,
                'title'     : None,
                'pubDate'   : None,
                'author'    : None}

        text = None
        try:
            if len(i.content)>1: 
                logger.info("Have more contents.\tCONTENTS:%d", len(i.content))
            if i.content[0]['type'] != "text/plain":
                text = bte.html2text(i.content[0]['value'])
            else:
                text = i.content[0]['value']
        except AttributeError:
            text = i.get('emm_text') # for medisys
            if not text:
                text = i.get('summary')
                if not text:
                    logger.info('No TEXT founded!')
                    text = ""
        # assert: `text` is defined, may be empty string
        assert text is not None

        # prepare `guid`
        hash_id = False
        try: id = i.id
        except AttributeError:
            hash_id = True
        if (hash_id or i.id==""):
            id = hashlib.sha224(text).hexdigest()
        assert id

        item['guid'] = id
        item['text'] = text
        # copy
        # copy 'to this' : ['first OK from list','']
        copy = {"title"     : ["title"],
                "link"      : ["link"],
                "pubDate"   : ["published_parsed", "updated_parsed", "created_parsed"],
                "author"    : ["author"]}
        for key in copy:
            set = False
            for value in copy[key]:
                try: item[key] = i[value]
                except KeyError: pass
                else : set = True
            if not set:
                logger.debug("TAG:%s was not set for ID:%s", key, id)
                item[key] = ""
        # assert - for each key from `copy` item has same key with value - value
        # may be empty ""

        # author -> author/name or keep author empty
        if item['author']:
            author_name = item['author']
            item['author'] = {'name':author_name}

        #item['pubDate'] = date2ISO(item['pubDate'])

        result['items'].append(item)
        result['items_count'] += 1
    return result
