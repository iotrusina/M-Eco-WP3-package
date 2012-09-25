import threading
import time
from webrss.model.feed import Feed
import random
from webrss.download import getDataFrom
from webrss.shared_func import writeToFile
from webrss.codegenerator import CodeGenerator
import os
import sys
import cherrypy



download_folder = "/mnt/minerva1/nlp/projects/spinn3r/solr_data/xjerab13"
backup_folder = "rss_backup"
#download_folder = "download"

class Core(threading.Thread):
    
    
    
    def __init__(self, group=None, target=None, name=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name, verbose=verbose)
        self.status = "idle"
        self.running = False
        self.jobs = []
        self.active_jobs = []
        self.myname = name
    
    def loadJobs(self):
        f = Feed.findAll()
        for fd in f:
            if fd.enable:
                fd.thr = None
                self.addJob(fd)
    
    def addJob(self, fd):
        fd.status = "idle"
        fd.thr = None
        self.jobs.append(fd)
    
    def removeJob(self, item_id):
        for f in range(len(self.jobs)):
            if self.jobs[f].id == int(item_id):
                self.jobs[f].status = "deactivating..."
                if self.jobs[f].thr:
                    if self.jobs[f].thr.isAlive():
                        self.jobs[f].thr.join()
                j = self.jobs.pop(f)
                j.save()
                return
            
    def updateJob(self, job):
        item_id = job.id
        for f in range(len(self.jobs)):
            if self.jobs[f].id == int(item_id):
                if self.jobs[f].thr:
                    if self.jobs[f].thr.isAlive():
                        self.jobs[f].thr.join()
                self.jobs[f].updateFromJob(job)
                
    
    def getJobs(self):
        return self.jobs
    
    def worker(self, job):
        try:
            job.status = "downloading"
            feed = getDataFrom(job.url, job.logon, job.password)
            if job.backup:
                writeToFile(feed, job.name, backup_folder, extension='xml', timestamp=True)
            modulename = CodeGenerator.getClassName(job)
            m = __import__(modulename)
            output = m.Downloader().parseFeed(job, feed)
            if output:
                writeToFile(output, job.name, download_folder, extension="xml", timestamp=True)
            job.status = "idle"
        except Exception, e:
            cherrypy.log("error when parsing feed id %s name %s"%(str(job.id),job.name))
            cherrypy.log(str(e))
            #job.enable = 0
        finally:
            job.status = "idle"
            job.last_update = time.time()
            job.save()
            job.thr = None
    
    def run(self):
         
        ppath = os.path.join(sys.path[0], "webrss", "downloaders")
                    
        if not ppath in sys.path:
            sys.path.append(ppath)
        
        self.status = "running"
        self.running = True
        while(self.running):
            now = time.time()
            for f in self.jobs:
                #print f.thr
                if f.enable == 0:
                    self.removeJob(f.id)
                    continue
                if (f.last_update + f.update_time ) < now and f.status == "idle":
                    t = threading.Thread(target=self.worker, args=(f,))
                    self.active_jobs.append(t)
                    f.thr = t
                    t.start()
                
            time.sleep(5)
            self.active_jobs = [t for t in self.active_jobs if not t.isAlive()]
                
    def stop(self):
        cherrypy.log("%s THREAD - Waiting for child threads to terminatte..."%(self.myname.upper()))
        self.status = "stoped"
        self.running = False
        for f in self.jobs:
            f.status = "stopping"
            if f.thr:
                if f.thr.isAlive():
                    cherrypy.log("%s THREAD - Waiting for thread worker for %s"%(self.myname.upper(),f.name))
                    f.thr.join()
        cherrypy.log("%s THREAD - STOPPED"%(self.myname.upper()))    
            

        