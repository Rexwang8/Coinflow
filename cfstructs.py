from enum import Enum

class usrconfigjson():
    name = ''
    
    def __init__(self, name="DefaultName"):
        self.name = name

class acconfigjson():
    name = ''
    actype = ''
    startingBal = 0
    
    def __init__(self, name="", actype="", startingBal=0):
        self.name = name
        self.actype = actype
        self.startingBal = startingBal
        
class pgrmconfigjson():
    defaultWindow_w = 1200
    defaultWindow_h = 800
    defaultUser = 'u_rex'
    defaultAccount = 'a_chasechecking'
    defaultIsFullScreen = False
    defaultL2TransactionAmount = 100
    defaultL3TransactionAmount = 1000
    defaultDataFolderName = 'data'
    defaultconfigFileName = 'config.json'
    defaultbackupFolderName = 'backup'
    defaultrulesFileName = 'rules.txt'
    defaultcategoriesFileName = 'categories.txt'
    defaultstocksFileName = 'stocks.txt'
    
    def __init__(self):
        self.defaultWindow_w = 1200
        self.defaultWindow_h = 800
        self.defaultUser = 'u_rex'
        self.defaultAccount = 'a_chasechecking'
        self.defaultIsFullScreen = False
        self.defaultL2TransactionAmount = 100
        self.defaultL3TransactionAmount = 1000
        self.defaultDataFolderName = 'data'
        self.defaultconfigFileName = 'config.json'
        self.defaultbackupFolderName = 'backup'
        self.defaultrulesFileName = 'rules.txt'
        self.defaultcategoriesFileName = 'categories.txt'
        self.defaultstocksFileName = 'stocks.txt'
    


class Logger():
    debugLevel = 'ERROR' # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    def __init__(self):
        self.debugLevel = 'ERROR'
    
    def log(self, msg, level='INFO'):
        msg = str(msg)
        header = f"[COINFLOW] {level}: "
        msg = header + msg
        #debug and info only currently,
        #if debuglevel=INFO, only print INFO
        if self.debugLevel == 'DEBUG':
            if level == 'DEBUG':
                print(msg)
            elif level == 'INFO':
                print(msg)
        #if debuglevel=DEBUG, print INFO, DEBUG
        elif self.debugLevel == 'INFO':
            if level == 'INFO':
                print(msg)
        #if debuglevel=WARNING, print INFO, DEBUG, WARNING
        elif self.debugLevel == 'WARNING':
            if level == 'WARNING':
                print(msg)
            elif level == 'INFO':
                print(msg)
            elif level == 'DEBUG':
                print(msg)
        #if debuglevel=ERROR, print INFO, DEBUG, WARNING, ERROR
        elif self.debugLevel == 'ERROR':
            if level == 'ERROR':
                print(msg)
            elif level == 'WARNING':
                print(msg)
            elif level == 'INFO':
                print(msg)
            elif level == 'DEBUG':
                print(msg)
    

