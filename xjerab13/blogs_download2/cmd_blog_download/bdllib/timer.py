import time
import logging

log = logging.getLogger("blog_download")


class Timer(object):
    '''Scheduler. Call functions after specified amount of time.'''
    def __init__(self, sleepTime = 0):
        self._sleepTime = sleepTime
        self._listOfFunctions = []
        log.debug("Timer was inicialized with repeat time: %d minutes.", self._sleepTime)
        
    def addFunction(self, func):
        self._listOfFunctions.append(func)
    
    def removeFunction(self,func):
        if func in self._listOfFunctions:
            self._listOfFunctions.remove(func)
        
    def start(self):
        while True:
            for func in self._listOfFunctions:
                func()
            if self._sleepTime > 0:
                self._sleeping()
            else:
                return
        
    def _sleeping(self):
        
        t = self._sleepTime
        #print "wating " + str(t)
        next_time = (time.time() + self._sleepTime * 60) 
        while time.time() < next_time:
            time.sleep(60)
            t -= 1
            #print "zbyva cca " + str(t)
            

    def setRepeatTime(self, rt):
        self._sleepTime = rt
    
    
        
