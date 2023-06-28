import csv
import datetime
import json
from enum import Enum
import os
import re

import cfstructs as cfs
import cfclassifier as cfc

class AccountType(Enum):
    Checking = 1
    Savings = 2
    Credit = 3
    Investment = 4
    Cash = 5
    
    def parseAccountType(type):
        type = type.strip().lower()
        if type == 'checking':
            return AccountType.Checking
        elif type == 'savings':
            return AccountType.Savings
        elif type == 'credit':
            return AccountType.Credit
        elif type == 'investment':
            return AccountType.Investment
        elif type == 'cash':
            return AccountType.Cash
        else:
            return None
        
    def __str__(self):
        if self == AccountType.Checking:
            return 'Checking'
        elif self == AccountType.Savings:
            return 'Savings'
        elif self == AccountType.Credit:
            return 'Credit'
        elif self == AccountType.Investment:
            return 'Investment'
        elif self == AccountType.Cash:
            return 'Cash'
        else:
            return 'Unknown'

class TransactionSource():
    dateStart = datetime.datetime.now()
    dateEnd = datetime.datetime.now()
    path = ''

class User():
    name = ''
    id = 0
    accounts = list()
    currentAccount = None
    budget = cfc.BudgetSet()
    path = ''
    
    
    def __init__(self, name='', id=0):
        self.name = name
        self.id = id
        self.accounts = list()
        self.path = f"data/{name}"
        
    def getAccountByName(self, name):
        name = name.lower().strip()
        for account in self.accounts:
            print(f"Account: {account.nameOfAccount} == {name}")
            if account.nameOfAccount == name:
                return account
        return None
    
    def addAccount(self, account):
        self.accounts.append(account)
        
    def countAccounts(self):
        return len(self.accounts)
    
    def countTransactions(self):
        c = 0
        for account in self.accounts:
            c += len(account.transactionsByDate)
        return c
        
    def getBudgetTransactions(self, days=30):
        transactions = dict()
        today = datetime.datetime.now()
        #get all transactions from 30 day rolling window, categorized and summed
        for account in self.accounts:
            for troot in account.transactionsByDate:
                dateofTransaction = datetime.datetime.strptime(troot.Date, '%m/%d/%Y')
                isThirtyDays = (today - dateofTransaction).days <= days
                key = f"{troot.AssumedCategory[0]}-{troot.AssumedCategory[1]}"
                if isThirtyDays:
                    if key in transactions:
                        transactions[key] += troot.Amount
                    else:
                        transactions[key] = troot.Amount
                        
        return transactions
    
class UserManifest():
    users = list()
    listOfUsernames = list()
    classifier = cfc.Classifier()
    usercount = 0
    totalAccounts = 0
    numSources = 0
    rules = cfc.RuleSet()
    cats = list()
    
    def __init__(self):
        self.users = list()
        self.listOfUsernames = list()
        
    def addUser(self, name):
        cfs.Logger().log(f"Adding User: {name}", 'INFO')
        self.users.append(User(name, len(self.users)))
        self.listOfUsernames.append(name)
        return len(self.users) - 1
    
    def loadUser(self, user):
        self.users.append(user)
        self.listOfUsernames.append(user.name)
        return len(self.users) - 1
        
    def getUser(self, id):
        for user in self.users:
            if user.id == id:
                return user
        return None
    
    def getUserByName(self, name):
        for user in self.users:
            if user.name == name:
                return user
        return None
    
    def listUsers(self):
        txt = ''
        for user in self.users:
            txt += f"{user.name}, {user.id}\n"
        return txt
    
    def listAllAccounts(self):
        txt = ''
        for user in self.users:
            for account in user.accounts:
                txt += f"({user.name}, {account.nameOfAccount})\n"
        return txt
    
    
    def addUserAccount(self, id, account):
        user = self.getUser(id)
        user.accounts.append(account)
        
    def setListOfUsernames(self):
        listOfUsernames = list()
        for user in self.users:
            listOfUsernames.append(user.name)
        self.listOfUsernames = listOfUsernames

class Transaction():
    CreditOrDebit = ''
    Date = ''
    Description = ''
    Amount = 0
    Type = ''
    Balance = 0
    CheckOrSlip = ''
    AssumedCategory = ('', '')
    AssumedCategoryType = 'income'
    labelledType = ''
    
    
    def __init__(self, CreditOrDebit, Date, Description, Amount, Type, Balance, CheckOrSlip):
        self.CreditOrDebit = CreditOrDebit
        self.Date = Date
        self.Description = Description
        self.Amount = Amount
        if type(Amount) is str:
            self.Amount = float(Amount.replace(',', ''))
        self.Type = Type
        self.Balance = Balance
        self.CheckOrSlip = CheckOrSlip
        
    def __str__(self):
        ret = f"CreditOrDebit: {self.CreditOrDebit}, Date: {self.Date}, Description: {self.Description}, Amount: {self.Amount}, Type: {self.Type}, Balance: {self.Balance}, CheckOrSlip: {self.CheckOrSlip}"
        ret += f", AssumedCategory: {self.AssumedCategory}"
        return ret
    
        
class Account():
    nameOfAccount = ''
    balance = 0
    pendingcredits = 0
    typeOfAccount = AccountType.Checking
    transactionsByDate = list()
    transactions = list()
    sources = list()
    path = ''
    
    
    
    def __init__(self, nameOfAccount, balance, pendingcredits, typeOfAccount):
        self.nameOfAccount = nameOfAccount
        self.balance = balance
        self.pendingcredits = pendingcredits
        self.typeOfAccount = typeOfAccount
        self.transactionsByDate = list()
        
    def setBalance(self, balance):
        self.balance = balance
        
    def setPendingCredits(self, pendingcredits):
        self.pendingcredits = pendingcredits
    
    def getBalance(self):
        return self.balance
    
    def calcBalance(self):
        for tranaction in self.transactionsByDate:
            self.balance += tranaction[1].Amount
        return self.balance
        
    def AddTransaction(self, transactions):
        for tranaction in transactions:
            self.transactionsByDate.append((tranaction.Date, tranaction))
            
    def calcBalanceByDate(self):
        
        #get a list of transactions ordered from earliest to latest
        transactionsbyearliestdate = list()
        for tranaction in self.transactionsByDate:
            transactionsbyearliestdate.append(tranaction)
        transactionsbyearliestdate.sort(key=lambda x: x[0])

        #starting at balance start amount, add all transactions until date, 
        #updating each transaction's balance
        for tranaction in transactionsbyearliestdate:
            self.balance += tranaction[1].Amount
            tranaction[1].Balance = self.balance
        

            
            
    
            
    def __str__(self):
        stringTranctions = ''
        for tranaction in self.transactionsByDate:
            stringTranctions += f"{tranaction[0]}: {tranaction[1].__dict__}\n"
        return f"nameOfAccount: {self.nameOfAccount}, balance: {self.balance}, pendingcredits: {self.pendingcredits}, typeOfAccount: {self.typeOfAccount}, transactionsByDate: {stringTranctions}"


            

def parseCSVChaseChecking(path):
    #load csv file
    transactions = list()
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        cfs.Logger().log(f"Reading file: {path}", 'INFO')
        for row in reader:
            #skip header
            if row[0] == 'Details':
                continue
            
            try:
                #try to type by looking at all rows,
                validtypes = ['DSLIP', 'DEBIT', 'WIRE_OUTGOING', 'ACH_DEBIT', 'WIRE_INCOMING', 'FEE_TRANSACTION', 'ACCT_XFER', 'ACH_CREDIT', 'QUICKPAY_DEBIT', 'QUICKPAY_CREDIT']
                foundtype = 'ACH_DEBIT'
                for r in row:
                    if r in validtypes:
                        foundtype = r
                        break
                
                #parse row
                creditOrDebit = row[0]
                date = row[1]
                #description can be multiple rows due to commas
                #desc should be the 3rd of 6 rows
                desc = ''
                numrows = len(row)
                
                #find balance row which is last row
                for i in range(numrows, 0, -1):
                    balrow = -1
                    #try to parse as float
                    try:
                        float(row[i])
                        assert(float(row[i]) > 0 and float(row[i]) < 1000000 and float(row[i]) != 1)
                        balrow = i
                    except:
                        pass
                    
                    if balrow != -1:
                        break
                    
                for i in range(2, balrow):
                    desc += row[i]
                desc = desc.replace('"', '')
                desc = re.sub('\s{2,}', ' ', desc) #remove multiple spaces
                ncolcount = balrow - 2
                amt = row[ncolcount]
                ncolcount += 1
                typeoftransaction = row[ncolcount]
                ncolcount += 1
                bal = row[ncolcount]
                ncolcount += 1
                
                transaction = Transaction(creditOrDebit, date, f"{desc}", amt, typeoftransaction, bal, '')
                transaction.labelledType = foundtype
                transactions.append(transaction)
            except:
                cfs.Logger().log(f"Error parsing as Chase Checking: {row}", 'ERROR')
                continue
        csvfile.close()
    return transactions

def parseCSVChaseCredit(path):
    #load csv file
    transactions = list()
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        cfs.Logger().log(f"Reading file: {path}", 'DEBUG')
        for row in reader:
            #skip header
            if row[0] == 'Transaction Date':
                continue
            
            try:
                transactionDate = row[0]
                postDate = row[1]
                description = row[2].replace('"', '').replace('&amp;', '&')
                #remove multiple spaces
                description = ' '.join(description.split())
                typeOfTransaction = row[4]
                amt = row[5]
                memo = row[6]
                tranaction = Transaction('Credit', postDate, description, amt, 'Credit', 0, '')
                transactions.append(tranaction)
            except:
                cfs.Logger().log(f"Error parsing as Chase Credit: {row}", 'ERROR')
                continue
        csvfile.close()
    cfs.Logger().log(f"Found {len(transactions)} transactions parsing as Chase Credit", 'INFO')
    return transactions

def creditAddRunningBalance(transactions, bal):
    transactions.sort(key=lambda x: x.Date)
    for tranaction in transactions:
        amt = float(tranaction.Amount)
        bal += round(amt, 2)
        tranaction.Balance = round(bal, 2)
    transactions.sort(key=lambda x: x.Date, reverse=True)
    return transactions
  

def parseRules(catlist, pgrmConfig: cfs.pgrmconfigjson):
    listOfCatNames = list()
    for cat in catlist:
        if not cat.isRoot:
            listOfCatNames.append(cat.cat)
    
    rulesPath = pgrmConfig.defaultrulesFileName
    defaultRulesPath = 'default_rules.txt'
    if not os.path.isfile(rulesPath):
        cfs.Logger().log(f"Error: rules.txt not found, using default rules", 'ERROR')
        if not os.path.isfile(defaultRulesPath):
            cfs.Logger().log(f"Error: default_rules.txt not found", 'ERROR')
            return
        else:
            rulesPath = defaultRulesPath
            #clone default rules
            os.system(f"cp {defaultRulesPath} {rulesPath}")
    
    rawRulesLines = list()
    rulesLines = list()
    rules = list()
    ruleSet = cfc.RuleSet()
    with open(rulesPath) as f:
        rawRulesLines = f.readlines()
        f.close()
    
    for line in rawRulesLines:
        line = line.strip()
        if line.startswith('#'):
            continue
        if line == '':
            continue
        rulesLines.append(line)
        
    for line in rulesLines:
        
        try:
            symbol = line[0]
            incsymbol = line[1]
            rule = line[2:].split(':')[0].strip()
            value = line[2:].split(':')[1].strip()
            ruleObj = cfc.Rule(symbol, incsymbol, rule, value)
            
            rules.append(ruleObj)
        except:
            cfs.Logger().log(f"Error: Invalid rule: {line}, skipping", 'ERROR')
            continue
        
    ruleSet.rules = rules
    ruleSet.ensureOneDefault()
    ruleSet.checkValidCategories(categories=catlist)
    return ruleSet

def parseCategories(cfg: cfs.pgrmconfigjson):
    path = cfg.defaultcategoriesFileName
    pathDefault = 'default_categories.txt'
    #check if file exists
    if not os.path.isfile(path):
        cfs.Logger().log(f"Error: categories.txt not found, using default categories", 'ERROR')
        if not os.path.isfile(pathDefault):
            cfs.Logger().log(f"Error: default_categories.txt not found", 'ERROR')
            return
        else:
            path = pathDefault
            #clone default categories
            os.system(f"cp {pathDefault} {path}")
    
    rawCategoryLines = list()
    with open(path) as f:
        rawCategoryLines = f.readlines()
        f.close()
        
    categoryLines = list()    
    for line in rawCategoryLines:
        line = line.strip()
        if line == '':
            continue
        if line.startswith('#'):
            continue
        categoryLines.append(line)
        
    catList = list()
    croot = ''
    rootSymbol = ''
    numRoots = 0
    numChildren = 0
    numTotal = 0
    for line in categoryLines:
        try:
            cobj = cfc.category()
            if line.startswith('-'):
                croot = line[1:]
                rootSymbol = '-'
                cobj.root = croot
                cobj.cat = croot
                cobj.isExpense = True
                cobj.isRoot = True
                numRoots += 1
            elif line.startswith('+'):
                croot = line[1:]
                rootSymbol = '+'
                cobj.root = croot
                cobj.cat = croot
                cobj.isIncome = True
                cobj.isRoot = True
                numRoots += 1
            elif line.startswith('='):
                croot = line[1:]
                rootSymbol = '='
                cobj.root = croot
                cobj.cat = croot
                cobj.isRoot = True
                cobj.isNeutral = True
                numRoots += 1
            elif line.startswith('>'):
                cobj.root = croot
                cobj.cat = line[1:]
                if rootSymbol == '-':
                    cobj.isExpense = True
                elif rootSymbol == '+':
                    cobj.isIncome = True
                elif rootSymbol == '=':
                    cobj.isNeutral = True
                numChildren += 1
            else:
                cfs.Logger().log(f"Error parsing rule line: {line}, skipping", 'ERROR')
                continue
            numTotal += 1
            catList.append(cobj)
        except:
            cfs.Logger().log(f"Error parsing line: {line}, skipping", 'ERROR')
            continue
    return catList
            

def findProgramConfig():
    #look for config file for the program
    pgrmConfig = cfs.pgrmconfigjson()
    path = os.getcwd()
    cfpath = os.path.join(path, 'config.json')
    if os.path.isfile(cfpath):
        with open(cfpath) as json_file:
            pgrmConfig.__dict__ = json.load(json_file)
            cfs.Logger().log(f"Found config file for program", 'INFO')
            json_file.close()
    else:
        #create config file if not found
        with open(cfpath, 'w') as json_file:
            json.dump(pgrmConfig.__dict__, json_file)
            cfs.Logger().log(f"Generated config file for program", 'INFO')
            json_file.close()
            
            
    return pgrmConfig

def findAllUserFolders(dataFolder):
    #look for all user folders
    userFolders = list()
    for folder1 in os.listdir(dataFolder):
        #check if folder is a file
        if os.path.isfile(dataFolder + folder1):
            continue
        userFolders.append(folder1)
    return userFolders

def findAllAccountFolders(accFolder):
    #look for all account folders
    accFolders = list()
    for folder2 in os.listdir(accFolder):
        #check if folder is a file
        if os.path.isfile(os.path.join(accFolder, folder2)):
            continue
        else:
            accFolders.append(folder2)
    return accFolders

def findUserConfig(usrPath, pgrmcfg : cfs.pgrmconfigjson):
    usrCfg = cfs.usrconfigjson()
    
    cfgpath = os.path.join(usrPath, pgrmcfg.defaultconfigFileName)
    if os.path.isfile(cfgpath):
        with open(cfgpath) as json_file:
            usrCfg.__dict__ = json.load(json_file)
            cfs.Logger().log(f"Found config file for user", 'INFO')
            json_file.close()
    else:
        with open(cfgpath, 'w') as json_file:
            json.dump(usrCfg.__dict__, json_file)
            cfs.Logger().log(f"Generated config file for user", 'INFO')
            json_file.close()
            
    return usrCfg
        
def findAccountConfig(accPath, pgrmcfg : cfs.pgrmconfigjson):
    accCfg = cfs.acconfigjson()
    cfgpath = os.path.join(accPath, pgrmcfg.defaultconfigFileName)
    if os.path.isfile(cfgpath):
        with open(cfgpath) as json_file:
            accCfg.__dict__ = json.load(json_file)
            cfs.Logger().log(f"Found config file for account", 'INFO')
            json_file.close()
    else:
        with open(cfgpath, 'w') as json_file:
            json.dump(accCfg.__dict__, json_file)
            cfs.Logger().log(f"Generated config file for account", 'INFO')
            json_file.close()
    return accCfg

def findAccountTransactions(accPath):
    tsources = list()
    for file in os.listdir(accPath):
        #only take csvs
        if file.endswith(".csv") or file.endswith(".CSV"):
            tsources.append(file)
    return tsources


def newParse():
    pgrmConfig = findProgramConfig()
    usrManifest = UserManifest()
    userList = list()
    usrFolders = findAllUserFolders(pgrmConfig.defaultDataFolderName)
    #load users and settings
    for usr in usrFolders:
        usrObj = User(id=usrManifest.usercount, name=usr)
        usrPath = os.path.join(pgrmConfig.defaultDataFolderName, usr)
        usrCfg = findUserConfig(usrPath, pgrmConfig)
        usrObj.path = usrPath
        usrManifest.usercount += 1
        
        #look for Budget file
        userBudget = cfc.BudgetSet() #default budget
        budgetPath = os.path.join(usrPath, 'budget.json')
        if os.path.isfile(budgetPath):
            with open(budgetPath) as json_file:
                userBudget.values = json.load(json_file)
                cfs.Logger().log(f"Found budget file for user: {usr}", 'INFO')
                json_file.close()
        
        usrObj.budget = userBudget
        
        
        #usrObj.config = usrCfg
        userList.append(usrObj)
        
    cfs.Logger().log(f"Found {len(userList)} users", 'INFO')
    #load accounts and transactions
    for usr in userList:
        usrname = usr.name
        accpath = usr.path
        accList = list()
        accList = findAllAccountFolders(accpath)
        accObjList = list()
        usrManifest.totalAccounts += len(accList)
        
        for acc in accList:
            cfs.Logger().log(f"Found account {acc} for user {usrname}", 'INFO')
            
            #load config
            accCfg = findAccountConfig(os.path.join(accpath, acc), pgrmConfig)
            typeOfAcc = AccountType.parseAccountType(accCfg.actype)
            cfs.Logger().log(f"Account type: {typeOfAcc}", 'INFO')
            
            sourcePath = os.path.join(accpath, acc)
            
            sourceList = list()
            sourceList = findAccountTransactions(sourcePath)
            usrManifest.numSources += len(sourceList)
            #print name of account
            cfs.Logger().log(f"Found {len(sourceList)} sources for account {usrname}/{acc}", 'INFO')
            
            accObj = Account(nameOfAccount=acc, typeOfAccount=typeOfAcc, balance=0, pendingcredits=0)
            accObj.sources = sourceList
            accObj.path = sourcePath
            accObj.typeOfAccount = typeOfAcc
            accObj.balance = accCfg.startingBal
            accObjList.append(accObj)
        usr.accounts = accObjList    
        cfs.Logger().log(f"Found {len(accObjList)} accounts for user {usrname}", 'INFO')
        
    #tally up totals
    numusers = usrManifest.usercount
    numaccs = usrManifest.totalAccounts
    numSources = usrManifest.numSources
    cfs.Logger().log(f"Found {numusers} users with {numaccs} accounts", 'INFO')
    cfs.Logger().log(f"Sourced from {numSources} files", 'INFO')
    
    #now that we have all the accounts, and sources, we can start parsing
    categories = list()
    categories = parseCategories(pgrmConfig)
    rules = parseRules(categories, pgrmConfig)
    classifier = cfc.Classifier2(categories, rules)
    
    cfs.Logger().log(f"Found {len(categories)} categories and {len(rules)} rules", 'INFO')
    for usr in userList:
        if len(usr.accounts) == 0:
            continue
        for acc in usr.accounts:
            if len(acc.sources) == 0:
                continue
            cfs.Logger().log(f"Parsing transactions for user {usr.name}/{acc.nameOfAccount}", 'INFO')
            
            #parse any existing sources
            transactions = list()
            for source in acc.sources:
                cfs.Logger().log(f"Parsing source {source}", 'DEBUG')
                spath = os.path.join(acc.path, source)
                cfs.Logger().log(f"Path: {spath}", 'DEBUG')
                stransactions = list()
                if acc.typeOfAccount == AccountType.Credit:
                    stransactions = parseCSVChaseCredit(spath)
                    stransactions = creditAddRunningBalance(stransactions, bal=acc.balance)
                elif acc.typeOfAccount == AccountType.Checking:
                    stransactions = parseCSVChaseChecking(spath)
                if stransactions == None or len(stransactions) == 0:
                    cfs.Logger().log(f"Failed to parse source {source}", 'ERROR')
                    continue
                    
                for t in stransactions:
                    transactions.append(t)
            
            #Populate transactions with categories
            for transaction in transactions:
                desc = transaction.Description
                root, cat, transactionType = classifier.classify(desc, transaction.Amount)
                transaction.AssumedCategory = (root, cat)
                transaction.AssumedCategoryType = transactionType
                
            acc.transactionsByDate = transactions
            
    #populate users with budgets
    for usr in userList:
        budgetset = cfc.BudgetSet(categories=categories) 
        budgetPath = os.path.join(usr.path, 'budget.json')
        if os.path.isfile(budgetPath):
            with open(budgetPath) as json_file:
                budgetset.values = json.load(json_file)
                cfs.Logger().log(f"Found budget file for user: {usr.name}", 'INFO')
                json_file.close()
        else:
            with open(budgetPath, 'w') as json_file:
                json.dump(budgetset.values, json_file)
                cfs.Logger().log(f"Generated budget file for user: {usr.name}", 'INFO')
                json_file.close()    
        budgetset.reconcileChangedBudgetFile(budgetPath)
        usr.budget = budgetset    
            
    usrManifest.users = userList
    usrManifest.rules = rules
    usrManifest.cats = categories
    usrManifest.setListOfUsernames() 
    #print(usrManifest.__dict__)     
    #print(usrManifest.__dict__['users'][0].__dict__)
    #print(usrManifest.__dict__['users'][1].__dict__)
    #print(usrManifest.__dict__['users'][0].__dict__["accounts"][0].__dict__)
    
    
    
           
    return usrManifest, pgrmConfig      


newParse()