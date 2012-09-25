from ConfigParser import SafeConfigParser
from bdllib.shared_func import makePath
from bdllib.exceptions import SettingsSectionNotFound


def loadSettings(settings, file, section = "default"):
    '''Load settings from file.
    
     Keyword arguments:
     settings - default settings from parrent class 
     file - abs path to file
     section - section name (default = default)
     '''
    ini_parser = SafeConfigParser()
    ini_parser.read(makePath(file))
    
    if not section in ini_parser.sections():
        msg = "V souboru %s nenalezena sekce %s." %(file, section)
        raise SettingsSectionNotFound(msg)
    
    for key in settings.keys():
            tmp = settings[key]
            if ini_parser.has_option(section, key):
                if type(settings[key]) == int:
                    tmp = ini_parser.getint(section, key)
                elif type(settings[key]) == bool:
                    tmp = ini_parser.getboolean(section, key)
                else:
                    tmp = ini_parser.get(section, key)

            settings[key] = tmp
