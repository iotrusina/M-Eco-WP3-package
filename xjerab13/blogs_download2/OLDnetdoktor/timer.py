import time

class Timer(object):
    def __init__(self, rt = 1):
        self._repeatTime = rt
        self._listOfFunctions = []
        
    def registerFunction(self, func):
        
        self._listOfFunctions.append(func)
        
    def start(self):
        while True:
            for func in self._listOfFunctions:
                func()
            if self._repeatTime > 0:
                self._sleeping()
            else:
                return
        
    def _sleeping(self):
        t = self._repeatTime
        #print "wating " + str(t)
        next_time = (time.time() + self._repeatTime * 60) 
        while time.time() < next_time:
            time.sleep(60)
            t -= 1
            print "zbyva cca " + str(t)
            

    def setRepeatTime(self, rt):
        self._repeatTime = rt
        
