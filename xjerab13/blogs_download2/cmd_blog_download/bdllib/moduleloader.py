import sys
import inspect 
import os
from bdllib.exceptions import EndOfChainError


class ModuleHandler(object):
    '''Container - load and hold all modules from folder'''
    def __init__(self):
        #list of loaded clases
        self.classHandler = []
        #list of loaded instances of classes
        self.instanceHandler = None
        
        #self._workddd = None
        #using list or chain
        self.storeType = None
    
    def loadModulesFrom(self,ppath, prefix):
        '''Loading modules from folder.
        
         Keyword arguments:
         ppath - path to folder with python modules
         prefix - classname preffix for target class selection
         
        '''
        
        prefix = prefix.lower()
        #need module path in PATH
        if not os.path.isabs(ppath):
            ppath = os.path.join(sys.path[0], ppath)
        
        folder = ppath
      
        if not folder in sys.path:
            sys.path.append(folder)
        #importing all .py files
        to_import = [f for f in os.listdir(folder) if f.endswith(".py")]
        for plugin in to_import:
            if plugin.endswith(".py"):
                name = plugin [:-3]
                __import__(name)
                cm = sys.modules[name]
                clist = inspect.getmembers(cm, inspect.isclass)
                #for all class, if class have correct preffix, make instance
                for c in clist:
                    classname, classlink = c
                    classname = classname.lower()
                    if classname.startswith(prefix):
                        self.classHandler.append(classlink)    
                        break


    
    def createListOfInstances(self, **params):
        self.storeType = "list"
        self.instanceHandler = []
        for clink in self.classHandler:
            instance = clink(**params)
            self.instanceHandler.append(instance)
    
    def createChainOfInstances(self, chainEndClass ,**params):
        if not chainEndClass:
            raise EndOfChainError("EndClass not specified")
        
        self.storeType = "chain"
        self.instanceHandler = chainEndClass(**params)
        for c in self.classHandler:
            tmp = c(**params)
            tmp.registerNextHandler(self.instanceHandler)
            self.instanceHandler = tmp
        
    #call all instances to make them work
    def work(self,**item):
        if self.storeType == "list":
            for instance in self.instanceHandler:
                instance.work(**item)
                
        elif self.storeType == "chain":
            self.instanceHandler.work(**item)
        
        
            
       
    
    
    
    