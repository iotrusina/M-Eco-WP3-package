#!/usr/bin/env python

from __future__ import with_statement
import sys, os
reload(sys)
sys.setdefaultencoding('utf-8')
try:
    import multiprocessing
except ImportError:
    multiprocessing = None
    import threading
else:
    threading = None
import subprocess
import logging
import logging.handlers
import time
import warnings
import traceback
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
from autoapi.connection import get_connection


import timer

NAME = 'master'

LOG_DIR = '/mnt/minerva1/nlp/projects/meco/mg4j/server/root/xrylko00/logs/'
LOG_FILENAME = 'master.txt'

# logging init
logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(NAME)


##############
# DECORATORS #
##############
class logDecorator(object):
    """
    Add `logger` to kwargs.
    If `__process` in kwargs use it for creating logger and then remove
    from kwargs.
    """
    def __init__(self, f):
        self.f = f
    def __call__(self, *args, **kwargs):
        numb = ''
        if kwargs.get('__process', None) != None:
            numb = '.%s' % kwargs['__process']
            del kwargs['__process']
        logger_name = 'master.' + self.f.__name__ + numb
        # logger for function
        kwargs['logger'] = logging.getLogger(logger_name)
        # logger for decorator
        self.logger = logging.getLogger(logger_name + '.@logDecorator')
        self.logger.debug('entering')
        retval = self.f(*args, **kwargs)
        self.logger.debug('leaving')
        return retval

def endlessDecorator(maxRuns):
    """
    Run function `maxRuns` times. If maxRuns is 0 runs unlimited times.
    If function ends or raise error log it as error.
    """
    def wrap(f):
        def ff(*args, **kwargs):
            # create logger for decorator
            logger_name = ''
            try:
                logger_name = kwargs['logger'].name
            except (KeyError, AttributeError):
                logger_name = 'master.%s.@endlesssDecorator' % str(f.__name__)
            else:
                logger_name = logger_name + '.@endlessDecorator'
            logger = logging.getLogger(logger_name)

            msg = "not set"
            runs = 0
            retval = None
            # if maxRuns is 0 then never ends
            # else runing is limited by maxRuns
            while not maxRuns or runs < maxRuns:
                runs += 1
                logger.debug('running %d. times' % runs)
                try:
                    retval = f(*args, **kwargs)
                except Exception, e:
                    file = StringIO.StringIO()
                    traceback.print_exc(15, file=file)                    
                    msg = 'endless function raise error {%s} ' % str(e)
                    msg += 'with traceback: \n{%s}' % file.getvalue()
                else:
                    msg = 'endless function return {%s}' % str(retval)
                logger.error(msg + ' in %d. run' % runs)
            return retval
        ff.__name__ = f.__name__
        return ff
    return wrap

#############
# FUNCTIONS #
#############

@logDecorator
@endlessDecorator(1)
def cron(crontab, logger):
    """
    Open `crontab` and run line per line (ignore empty lines and lines with leading #).
    """
    while True:

        file = open(crontab, 'r')
        scripts = [x.strip() for x in file]
        file.close()
        for x in scripts:
            x = x.strip()
            if not x.startswith('#') and x:
                logger.info('running {%s}' % x)
                #retval = subprocess.call(shlex.split(x), shell=True)
                retval = os.system(x)
                if retval:
                    logger.error('return value = {%s} for line {%s}' % (retval, x))

        #return
        logger.debug('going to sleep to tomorrow')
        timer.sleep_to_tomorrow()

@logDecorator
@endlessDecorator(1)
def keep_alive(script, logger, stdin=None, stdout=None, stderr=None):
    runs = 0
    while True:
        runs += 1
        logger.info('running script {%s}' % " ".join(script))
        try:
            p = subprocess.Popen(script, stdin=stdin, stdout=stdout, stderr=stderr)
        except OSError, e:
            logger.critical(e)
            return
        except Exception, e:
            logger.error(e)
            return
        p.wait()
        # script ends! Cry as much as it hurts 
        level = 0
        if p.returncode == 0 : level = logging.WARNING
        else                 : level = logging.ERROR
        logger.log(level, 'script {%s} ended %d. times and with return code {%d}' %\
                     (" ".join(script), runs, int(p.returncode)))
        True = False

@logDecorator
@endlessDecorator(1)
def analyzed(sys_path, logger):
    while True:
        try:
            p = subprocess.Popen(sys_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError, e:
            logger.critical(e)
            return
        except Exception, e:
            logger.error(e)
            return
        (stdout, stderr) = p.communicate()
        if p.returncode:
            logger.error('return code = {%s}' % p.returncode)
        logger.error('stderr = {%s}' % stderr.strip())
        logger.info('stdout = {%s}' % stderr.strip())
        #return
        logger.debug('going to sleep to tomorrow')
        timer.sleep_to_tomorrow()


@logDecorator
@endlessDecorator(1)
def url_stahovak(logger, sys_path, cursor):
    sys.path.append(sys_path)
    from db_url_stahovak import download_and_insert
    URL = 9
    while True:
        counter = 0
        LIMIT = 1
        cursor.execute("""select 
                        e.id, 
                        e.name, 
                        d.pubDate,
                        d.pubTime
                        from entities e, instances i, documents d
                        WHERE
                        e.enttype_id=%s
                        AND NOT EXISTS (SELECT * FROM downloadurl WHERE entity_id=e.id) 
                        AND i.entity_id=e.id -- JOIN
                        AND i.item_id=d.id   -- JOIN
                        ORDER BY (d.pubDate + d.pubTime)
                        LIMIT %s;""", (URL, LIMIT))
        instances = [i for i in cursor]
        if len( instances ) == 0:
            timer.sleep_to_tomorrow()
            continue
        for instance in instances:
            counter += 1
            entity_id, entity_name, doc_pubdate, doc_pubtime = instance
            print ">>>", str(counter), entity_id, entity_name, doc_pubdate
            document_id = download_and_insert(entity_name, doc_pubdate, doc_pubtime)
            print ">>>", document_id
            cursor.execute("""INSERT INTO downloadurl (entity_id, document_id)
                              VALUES (%s, %s)""", (entity_id, document_id))




@logDecorator
@endlessDecorator(3)
def stanford(logger, sys_path, cursor, offset=0, limit=200):
    # stanford should be last running always
    # TODO timer.sleep_minutes(120)
    while True:
        if not cursor:
            raise ValueError('Cursor is not set!')

        sys.path.append(sys_path)
        warnings.filterwarnings('ignore') # ignoring for import
        from stanford import analyze
        warnings.filterwarnings('default')
        cursor.execute("""select id from documents 
                          where termvector is null 
                                and (_stanford is null OR _stanford=%s)
                                and _calaised=%s
                                and language in (%s, %s)
                                and source_id in (select id from prefered_sources)
                          order by id desc
                          limit %s 
                          offset %s""", 
                        (False, True, "en", "de", limit, offset))
        #cursor.execute('select id from documents where termvector is null limit 50')
        OK = 0
        count = 0
        for row in cursor:
            count += 1
            id = row[0]
            logger.debug('analyzing id {%s}' % id)
            errmsg = analyze(int(id))
            if errmsg:
                logger.info('error message = {%s}' % errmsg)
            else:
                OK += 1
        logger.info('stanford analyzed: limit = {%s}, ok = {%s} => errors = {%s}' % \
                    (limit, OK, count-OK))
        if not count:
            #return
            logger.debug('going to sleep to tomorrow')
            timer.sleep_to_tomorrow()
        # and again!

    # end


"""
sys.path.append('../stahovak')
from stahovak.db_stahovak import main as db_stahovak
@logDecorator
@endlessDecorator
def stahovak(logger):
    for line in db_stahovak():
        logger.info('insert document id = {%s}' % str(line))
"""

#########
# TESTs #
#########
import random
@logDecorator
@endlessDecorator(2)
def testRaise(logger):
    timer.sleep(random.random())
    logger.debug('going to raise an error!')
    raise Exception("ouch!")
@logDecorator
@endlessDecorator(3)
def testReturn(logger):
    timer.sleep(random.random())
    logger.debug('going to return')
    return ['o', 'u', 'c', 'h']

########
# MAIN #
########
@logDecorator
def main(logger):
    conn = get_connection()

    if len(sys.argv) < 2:
        print "USAGE ./master.py JOB_NUMBER [JOB_NUMBER]+\nSee job_list in source code!"
        return 1

    jobs_list = []
    numbers = []

    for number in sys.argv[1:]:
        job_list_number = int(number)
        numbers.append(job_list_number)
        
        job_lists = {# Just for test 0: [(testRaise, (),{}), (testRaise, (), {}), # TEST
                #        (testReturn, (), {})],
                     1: [(cron, ('crontab',), {})],               # NORMAL
                     # Obsolete 2: [(stanford, (), {'cursor' : conn.cursor(), 'sys_path' : '../db'})],      
                     # Obsolete 3: [(analyzed, ('../stahovak/analyzed.py',), {})],
                     # Obsolete 4: [(url_stahovak, (), {'cursor' :conn.cursor(), 'sys_path' : '../stahovak'})],
                     }
        jobs_list += job_lists[job_list_number]

    #handler = logging.handlers.TimedRotatingFileHandler(
    #        LOG_DIR + "+".join(sys.argv[1:]) + "-" + LOG_FILENAME, when='D', interval=1, backupCount=3)
    #handler.setFormatter(logging.Formatter(fmt='%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s'))
    #logger.addHandler(handler)

    logger.info('Starting with jobs {%s}' % ', '.join(map(str, numbers)))

    jobs = []
    for i, todo in enumerate(jobs_list):
        (target, args, kwargs) = todo
        kwargs['__process'] = i
        if multiprocessing:
            p = multiprocessing.Process(target=target, args=args, kwargs=kwargs)
        else:
            p = threading.Thread(target=target, args=args, kwargs=kwargs)
        jobs.append((p, todo))
        p.start()
    for job, (etc) in jobs:
        job.join()
    return 0

if __name__ == '__main__':
    sys.exit(main())
