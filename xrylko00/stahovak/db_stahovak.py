#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
#
# Copyright 2010 Vojtech Rylko
#

"""
Stahovak - configurable RSS/Atom feed downloader.

stdout: new inserted document's id per line
stderr: logging output
"""

__author__ = "xrylko00@stud.fit.vutbr.cz"
 
import sys
import socket
import logging
from optparse import OptionParser
import time

import timer
import db_downloader as downloader
from rytools import control_chars
# db
from autoapi.autoapi import *
from autoapi.connection import get_connection
import psycopg2

# classifier
import parser
sys.path.append("/mnt/minerva1/nlp/projects/twitter_classification/TwitterClassifier")
from tweetclassify import TwitterClassifier

from termvector import get_termvector

# socket timeout
timeout = 10
socket.setdefaulttimeout(timeout)

###
### SETTINGS
###
# in seconds:
SLEEP_TIME = 10*60
MIN_SCORE = 0.2 # for classifier
logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s')

def tuple2str(tuple):
    if not tuple: return tuple
    return ",".join(map(str, tuple))

def str2tuple(str):
    if not str: return str
    return tuple(map(int, str.split(",")))

def main():
    # logging init
    logger = logging.getLogger("db_stahovak")
    logger.setLevel(logging.WARNING)

    # start infoo
    logger.info("START") 
    
    # classifier
    tcl = TwitterClassifier()

    # get twitter's id's - only twitter should be classified
    conn = get_connection();
    cursor = conn.cursor()

    cursor.execute("select id from sources_twitter")
    twitter_ids = [id[0] for id in cursor]

    while True:
        # feeds init
        # XXX - performance problems - sources should be before while...
        sources = MSources()
        sources.get_multi(where="_stahovak = true")
        feeds = [Sources(**data) for data in sources.value()]
        assert feeds
        items_count = 0
        for source in feeds:
            logger.info("SOURCE\tSECTION:%s\tLINK:%s" % (source.get_section(), source.get_link()))
            modified = str2tuple(source.get_modified())
            data = downloader.download(source.get_link(), 
                                       source.get_etag(), 
                                       modified)
            # update etag/modified
            if data['etag'] or data['modified']:
                diff = False
                if source.get_etag() != data['etag']:
                    diff = True
                    source.set_etag(data['etag'])
                if modified != data['modified']:
                    diff = True
                    source.set_modified(tuple2str(data['modified']))
                if diff:
                    source.update()

            classified_as_irelevant = 0
            # work with items
            for item in data['items']:
                items_count += 1
                # prepare new database insert
                Item = Documents()
                Item.set_timestamp(timer.timestamp())
                Item.set_source_id(source.get_id())
                Item.set_language(source.get_language())

                Item.set_title(control_chars.remove(item['title']))
                Item.set_text(control_chars.remove(item['text']))

                try:
                    Item.set_termvector(get_termvector(
                        Item.get_text(), Item.get_language(),
                        conn))
                except psycopg2.ProgrammingError, e:
                    print str(e)
                    continue

                Item.set__relevance(None)
                
                # we classify only twitter's documents
                if ( source.get_id() in twitter_ids ):
                    score = tcl.classify(Item.get_text(), Item.get_language())
                    was_classified = (score != -1)
                    if (was_classified and score < MIN_SCORE):
                        # skip
                        classified_as_irelevant += 1
                        continue
                    if ( was_classified ):
                        Item.set__relevance(int(score * 100))


                Item.set_link(control_chars.remove(item['link']))
                Item.set_guid(source.get_section()+":"+control_chars.remove(item['guid']))

                if item['pubDate']:
                    pubDate = time.strftime("%Y-%m-%d", item['pubDate'])
                    if pubDate : Item.set_pubDate(pubDate)
                    pubTime = time.strftime("%H:%M:%S%z", item['pubDate'])
                    if pubTime :Item.set_pubTime(pubTime)
                if not Item.get_pubDate():
                    # dont want items without pubdate
                    continue

                ## following links
                if source.get__follow():
                    url = item['link']
                    logger.debug("Following LINK:%s", url)
                    page = downloader.download_url(url)
                    Item.set_text(control_chars.remove(page.get('text', '')))
                    Item.set_html_description(control_chars.remove(page.get('description', "")))
                    Item.set_html_keywords(control_chars.remove(page.get('keywords', "")))

                # insert it
                if Item.get_text():
                    inserted, id = Item.insert()
                    if inserted:
                        logger.debug("Document succesfully inserted into db with id=%s" % Item.get_id())
                        yield str(id) # output
                    else:
                        logger.debug("Document already in db with id=%s" % id)
                else:
                    logger.info("Item has not text!")

            # outputting
            logger.info("Created OUTPUT\tITEMS:%d\tIRELEVANT:%d", data['items_count'], classified_as_irelevant)
        if not items_count:
            print "going to sleep"
            timer.sleep_second(SLEEP_TIME)

if __name__ == "__main__":
    for line in main():
        print line
 
