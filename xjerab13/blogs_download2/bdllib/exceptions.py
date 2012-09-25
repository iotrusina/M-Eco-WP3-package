

class SettingsSectionNotFound(Exception):
    '''Setion in settings file does not exist'''
    def __init__(self, value):
        self.msg = value
    def __str__(self):
        return repr(self.msg)
    
    
class EndOfChainError(Exception):
    '''Chain of responsibility is not properly ended.'''
    def __init__(self, value):
        self.msg = value
    def __str__(self):
        return repr(self.msg)

class CacheDataException(Exception):
    '''Something terribly wrong happend to data in cache'''
    def __init__(self, value):
        self.msg = value
    def __str__(self):
        return repr(self.msg)
        