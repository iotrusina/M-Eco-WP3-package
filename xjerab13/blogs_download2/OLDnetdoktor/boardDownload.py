from netdoktor import NetDoktorHandler 

class BoardDownloader(object):
    def __init__(self):
        self._listOfHandlers = []
        self._listOfHandlers.append(NetDoktorHandler())
        
        pass

    def _wrapper(self):
        for hndl in self._listOfHandlers:
            hndl.run()
        pass

    def getWrapper(self):
        return self._wrapper