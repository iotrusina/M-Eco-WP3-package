import threading
import time
from webrss.model.feed import Feed
import random
from webrss.download import getDataFrom
from webrss.shared_func import writeToFile






class Core(threading.Thread):
    
    
    
    def __init__(self, group=None, target=None, name=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name, verbose=verbose)
        self.status = "idle"
        self.running = False
        self.jobs = []
        self.active_jobs = []
    
    def loadJobs(self):
        f = Feed.findAll()
        for fd in f:
            self.addJob(fd)
    
    def addJob(self, fd):
        fd.status = "idle"
        self.jobs.append(fd)
    
    def removeJob(self):
        pass
    
    def getJobs(self):
        return self.jobs
    
    def worker(self, job):
        job.status = "downloading"
        feed = getDataFrom(job.url, job.logon, job.password)
        writeToFile(feed, job.name, "download", extension="xml", timestamp=True)
        job.last_update = time.time()
        job.status = "idle"
        job.save()
    
    def run(self):
        self.status = "running"
        self.running = True
        while(self.running):
            now = time.time()
            for f in self.jobs:
                if (f.last_update + f.update_time ) < now and f.status == "idle":
                    t = threading.Thread(target=self.worker, args=(f,))
                    self.active_jobs.append(t)
                    t.start()
            time.sleep(5)
            self.active_jobs = [t for t in self.active_jobs if not t.isAlive()]
                
    def stop(self):
        print "exiting core"
        self.status = "stoped"
        self.running = False
        for f in self.jobs:
            f.status = "stopped"