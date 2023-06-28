
##classifier stuff

'''
To add a new category, go to the transactionClasses class and add a new field

To add a new definition, go to the __init__ function in the Classifier() and 
add a new definition based on previous definitions (exact or partial match)

'''



import datetime
from enum import Enum
import json





class category():
    root = ''
    isRoot = False
    cat = ''
    isIncome = False
    isExpense = False
    isNeutral = False

    
    
class RuleTypes(Enum):
    Specific = 1
    Exact = 2
    Partial = 3
    Default = 4
    
class RuleSet():
    rules = list()
    defaultRuleSet = False
    
    def ensureOneDefault(self):
        if self.defaultRuleSet == True:
            return
        newRules = list()
        for rule in self.rules:
            if rule.ruleType != RuleTypes.Default:
                newRules.append(rule)
                continue
            
            #remove all other default rules
            if self.defaultRuleSet == False:
                self.defaultRuleSet = True
                newRules.append(rule)
            else:
                print(f"[CoinFlow] Warning: Multiple default rules found. Only the first default rule will be used.")
                
    def checkValidCategories(self, categories):
        dictOfCategories = dict()

        for category in categories:
            if category.isRoot == True:
                dictOfCategories[category.root] = list()     
        for category in categories:
            if category.isRoot == False:
                dictOfCategories[category.root].append(category.cat)
                

        newRules = list()        
        for rule in self.rules:
            ruleToCat = rule.ruleMatchValue.split('-')[1].strip()
            ruleToRoot = rule.ruleMatchValue.split(' - ')[0].strip()
            isInDict = False
            
            if ruleToRoot in dictOfCategories:
                ldict = dictOfCategories[ruleToRoot]
                if ruleToCat in ldict:
                    isInDict = True
                    

            if isInDict:
                newRules.append(rule)
            else:
                print(f"[CoinFlow] Warning: Rule {rule.rulestr} does not have a valid category. Rule will not be used.")
        self.rules = newRules
        
                
    #for length, use len(self.rules)
    def __getitem__(self, index):
        return self.rules[index]
    def __len__(self):
        return len(self.rules)
                
            
    
    
class Rule():
    symbol = ''
    incsymbol = ''
    rulestr = ''
    ruleType = ''
    ruleMatchType = ''
    ruleMatchValue = ''
    rulematchwithtype = ''
    
    def __init__(self, symbol, inc, rulestr, ruleMatchValue):
        self.symbol = symbol
        self.incsymbol = inc
        self.rulestr = rulestr
        self.ruleMatchValue = ruleMatchValue
        self.parseRule()
        
    def parseRule(self):
        if self.symbol == 's':
            self.ruleType = RuleTypes.Specific
            self.ruleMatchType = 'ID'
        elif self.symbol == 's':
            self.ruleType = RuleTypes.Specific
            self.ruleMatchType = 'Date'
            self.rulestr = datetime.datetime.strptime(self.rulestr, '%m/%d/%Y')
        elif self.symbol == 'e':
            self.ruleType = RuleTypes.Exact
            self.ruleMatchType = 'Description'
        elif self.symbol == 'p':
            self.ruleType = RuleTypes.Partial
            self.ruleMatchType = 'Description'
        elif self.symbol == 'd':
            self.ruleType = RuleTypes.Default
            self.ruleMatchType = 'Description'
            
        if self.incsymbol == 'i':
            self.rulematchwithtype = 'income'
        elif self.incsymbol == 'e':
            self.rulematchwithtype = 'expense'
        elif self.incsymbol == 'n':
            self.rulematchwithtype = 'neutral'
        elif self.incsymbol == 'a':
            self.rulematchwithtype = 'all'
    
        
class Classifier2():
    ruleSet = RuleSet()
    categories = list()
    
    def __init__(self, categories, ruleSet):
        print(type(ruleSet))
        self.categories = categories
        self.ruleSet = ruleSet
        
    def classify(self, desc, amt):
        category = ''
        root = ''
        
        #check for specifc rules
        #not implemented
        #check for exact rules
        root, category = self.classifyByExact(desc, amt)
        if root != '' and category != '':
            return root, category, self.mapRootToIncome(root)
        root, category = self.classifyByPartial(desc, amt)
        if root != '' and category != '':
            return root, category, self.mapRootToIncome(root)
        root, category = self.classifyByDefault(desc)    
        #check for partial rules
        #check for default rules    
        return root, category, self.mapRootToIncome(root)
        
    def classifyByExact(self, desc, amt):
        exactRules = list()
        for rule in self.ruleSet.rules:
            if rule.ruleType == RuleTypes.Exact:
                exactRules.append(rule)
        for rule in exactRules:
            if amt > 0 and (rule.rulematchwithtype != 'income' and rule.rulematchwithtype != 'all'):
                continue
            if amt < 0 and (rule.rulematchwithtype != 'expense' and rule.rulematchwithtype != 'all'):
                continue
            if amt == 0 and (rule.rulematchwithtype != 'neutral' and rule.rulematchwithtype != 'all'):
                continue
            ruleRoot = rule.ruleMatchValue.split(' - ')[0].strip()
            ruleCat = rule.ruleMatchValue.split(' - ')[1].strip()
            ruleMatch = rule.rulestr.lower().strip()
            #print(f"Attempting match for {ruleMatch} to {desc.lower().strip()}")
            isMatch = False
            if rule.ruleMatchType == 'Description':
                if rule.rulestr == desc.lower().strip():
                    isMatch = True
            
            if isMatch:
                #print(f"Exact Matched {rule.rulestr} to {desc}")
                return ruleRoot, ruleCat
            #print(f"[CoinFlow] Exact Rule: {rule.rulestr}, {rule.ruleMatchValue}")
        return '', ''
    
    def classifyByPartial(self, desc, amt):
        partialRules = list()
        for rule in self.ruleSet.rules:
            if rule.ruleType == RuleTypes.Partial:
                partialRules.append(rule)
                
        for rule in partialRules:
            if amt > 0 and (rule.rulematchwithtype != 'income' and rule.rulematchwithtype != 'all'):
                continue
            if amt < 0 and (rule.rulematchwithtype != 'expense' and rule.rulematchwithtype != 'all'):
                continue
            if amt == 0 and (rule.rulematchwithtype != 'neutral' and rule.rulematchwithtype != 'all'):
                continue
            
            ruleRoot = rule.ruleMatchValue.split(' - ')[0].strip()
            ruleCat = rule.ruleMatchValue.split(' - ')[1].strip()
            ruleMatch = rule.rulestr.lower().strip()
            ruleDesc = desc.lower().strip()
            isMatch = False
            if rule.ruleMatchType == 'Description':
                if ruleMatch in ruleDesc:
                    isMatch = True
                    
            if isMatch:
                #print(f"Partial Matched {rule.rulestr} to {desc}")
                return ruleRoot, ruleCat
        return '', ''
    
    def classifyByDefault(self, desc):
        for rule in self.ruleSet.rules:
            if rule.ruleType == RuleTypes.Default:
                defaultRule = rule
                ruleRoot = defaultRule.ruleMatchValue.split(' - ')[0].strip()
                ruleCat = defaultRule.ruleMatchValue.split(' - ')[1].strip()
                print(f"Default Matched: {ruleRoot} - {ruleCat} to {desc}")
        
                return ruleRoot, ruleCat
        return 'Misc', 'Error'
    
                
        
    def mapRootToIncome(self, root):
        #maps root to 'income', 'expense' or 'neutral'
        isIncome = False
        isExpense = False
        isNeutral = False
       
        for cat in self.categories:
            #print(cat.cat)
            if root in cat.cat:
                if cat.isIncome:
                    return 'income'
                elif cat.isExpense:
                    return 'expense'
                elif cat.isNeutral:
                    return 'neutral'
                else:
                    return 'unknown'

        

class tranactionClasses():
    #costs money
    
    #shopping - offline
    Shopping = ("Shopping")
    ShoppingTools = ("Shopping - Tools")
    ShoppingGarden = ("Shopping - Garden")
    ShoppingFurniture = ("Shopping - Furniture")
    ShoppingHome = ("Shopping - Home")
    ShoppingElectronics = ("Shopping - Electronics")
    ShoppingOffice = ("Shopping - Office Supplies")
    ShoppingBooks = ("Shopping - Books")
    ShoppingMovies = ("Shopping - Movies")
    ShoppingMusic = ("Shopping - Music")
    ShoppingGames = ("Shopping - Games")
    ShoppingToys = ("Shopping - Toys")
    ShoppingBaby = ("Shopping - Baby")
    
    #personal - self improvement, entertainment, etc
    Personal = ("Personal")
    PersonalGeneral = ("Personal - General")
    PersonalGym = ("Personal - Gym")
    PersonalHair = ("Personal - Hair")
    PersonalCosmetics = ("Personal - Cosmetics")
    PersonalBaby = ("Personal - Baby")
    PersonalEntertainment = ("Personal - Entertainment")
    
    #Food
    Food = ("Food")
    FoodFast = ("Food - Fast Food")
    FoodDining = ("Food - Dining")
    FoodDelivery = ("Food - Delivery")
    FoodPet = ("Food - Pet")
    ShoppingGrocery = ("Shopping - Grocery")
    
    #Online - Subscriptions, Services, Shopping
    Online = ("Online")
    OnlineSubscriptions = ("Online - Subscriptions")
    OnlineServices = ("Online - Services")
    OnlineShopping = ("Online - Shopping")
    
    #bills
    BillsAndUtilities = ("Bills and Utilities")
    BillsAndUtilitiesElectric = ("Bills and Utilities - Electric")
    BillsAndUtilitiesWater = ("Bills and Utilities - Water")
    BillsAndUtilitiesInternet = ("Bills and Utilities - Internet")
    BillsAndUtilitiesPhone = ("Bills and Utilities - Phone")
    BillsAndUtilitiesCable = ("Bills and Utilities - Cable")
    BillsAndUtilitiesOther = ("Bills and Utilities - Other")
    
    #clothes sub categories
    Clothing = ("Clothing")
    ClothingShoes = ("Clothing - Shoes")
    ClothingAccessories = ("Clothing - Accessories")
    
    #Medical
    Medical = ("Medical")
    MedicalPrimary = ("Medical - Primary Care")
    MedicalDental = ("Medical - Dental")
    MedicalSpecialty = ("Medical - Specialty Care")
    MedicalUrgentCare = ("Medical - Urgent Care")
    MedicalMedications = ("Medical - Medications")
    MedicalMedicalDevices = ("Medical - Medical Devices")
    
    #Insurance
    Insurance = ("Insurance")
    InsuranceHome = ("Insurance - Home")
    InsuranceAuto = ("Insurance - Auto")
    InsuranceLife = ("Insurance - Life")
    InsuranceRenter = ("Insurance - Renter")
    InsuranceDisability = ("Insurance - Disability")
    InsuranceOther = ("Insurance - Other")
    
   
    #Home
    Home = ("Home")
    HomeRent = ("Home - Rent")
    HomeRepairs = ("Home - Repairs")
    HomeHOAFees = ("Home - HOA Fees")
    OtherTaxes = ("Other - Taxes")
    
    #Savings
    SavingsGeneral = ("Savings - General")
    SavingsEmergency = ("Savings - Emergency")
    SavingsRetirement = ("Savings - Retirement")
    SavingsInvestments = ("Savings - Investments")
    
    
    
    #Transportation
    Transportation = ("Transportation")
    TransportationCar = ("Transportation - Car")
    TransportationGas = ("Transportation - Gas")
    TransportationRepairs = ("Transportation - Repairs")
    TransportationParking = ("Transportation - Parking")
    
    #Debt
    DebtGeneral = ("Debt - General")
    DebtPersonal = ("Debt - Personal Loan")
    DebtStudent = ("Debt - Student Loan")
    DebtCreditCard = ("Debt - Credit Card")
    DebtAuto = ("Debt - Auto")
    DebtMortgage = ("Debt - Mortgage")
    
    OneTime = ("One Time")
    OtherExpenses = ("Expenses - Other")
    Gifts = ("Gifts")
    Donations = ("Donations")
    Entertainment = ("Entertainment")
    EntertainmentAlcohol = ("Entertainment - Alcohol")
    EntertainmentDrugs = ("Entertainment - Drugs")
    EntertainmentDating = ("Entertainment - Dating")
    EntertainmentGambling = ("Entertainment - Gambling")
    TravelConcerts = ("Travel - Concerts")
    TravelGeneral = ("Travel - General")
    TravelVacation = ("Travel - Vacation")
    TravelBusiness = ("Travel - Business")
    
    BankVerification = ("Other - Bank Verification")
    ExpenseTransfer = ("Expense - Transfer")
    Expense = ("Expense")
    
    Cash = ("Cash")
    Other = ("Other")
    OtherFees = ("Other - Fees")
    
    #gives money
    IncomeGifts = ("Income - Gifts")
    IncomeDividends = ("Income - Dividends")
    IncomePaycheck = ("Income - Paycheck")
    IncomeBonus = ("Income - Bonus")
    IncomeInterest = ("Income - Interest")
    IncomeRefunds = ("Income - Refunds")
    IncomeReimbursements = ("Income - Reimbursements")
    IncomeRental = ("Income - Rental")
    IncomeTransfer = ("Income - Transfer")
    IncomeOther = ("Income - Other")
    Income = ("Income")
    
    def returnListOfClasses(self):
        classes = list()
        for field in dir(tranactionClasses):
            if not field.startswith("__") and not field.startswith("returnListOfClasses"):
                
                #get the value of the string
                vstr = getattr(tranactionClasses, field)
                #classes.append(getattr(tranactionClasses, field))
                #create tuple of root class and category, root class has no dash
                if '-' in vstr:
                    root = vstr.split('-')[0].strip()
                    cat = vstr.split('-')[1].strip()
                    classes.append((root, cat))
                else:
                    classes.append((vstr, vstr))
                    
        return classes
    
    
class baseDefinitions():
    RootClass = tranactionClasses.Other
    Category = tranactionClasses.Other
    exactMatch = dict()
    partialMatch = dict()
    
    def addExactMatch(self, key, value):
        self.exactMatch[key] = value
    def addPartialMatch(self, key, value):
        self.partialMatch[key] = value
    
    def attemptExactMatch(self, matchString):
        for key in self.exactMatch:
            if key == matchString:
                return self.Category, self.RootClass
        return None, None
        
    def attemptPartialMatch(self, matchString):
        for key in self.partialMatch:
            if key in matchString:
                return self.Category, self.RootClass
            
        return None, None
        
    def getRootClass(self):
        return self.RootClass
    
    def attemptMatch(self, matchString):
        matchString = matchString.lower().strip()
        match, root = self.attemptExactMatch(matchString)
        if match is not None and root is not None:
            return str(match), root
        match, root = self.attemptPartialMatch(matchString)
        if match is not None and root is not None:
            return str(match), root
        return '', ''
        
    def __init__(self, rootClass = tranactionClasses.Other, category = tranactionClasses.Other):
        self.RootClass = rootClass.strip()
        self.Category = category.split('-')[1].strip()
        self.partialMatch = dict()
        self.exactMatch = dict()
        
class Classifier():
    AllCategories = list()  
    def ClassifyDescription(self, description):
        assumed = ''
        for category in self.AllCategories:
            assumed = category.attemptMatch(description)
            if assumed != ('', ''):
                return assumed
            
        return assumed
    
    def __init__(self):
        cat_IncomePayroll = baseDefinitions(tranactionClasses.Income, tranactionClasses.IncomePaycheck)
        cat_IncomePayroll.addPartialMatch("coreweave", tranactionClasses.IncomePaycheck)
        cat_IncomePayroll.addPartialMatch("remote online deposit", tranactionClasses.IncomePaycheck)
        self.AllCategories.append(cat_IncomePayroll)
        
        cat_IncomeTransfer = baseDefinitions(tranactionClasses.Income, tranactionClasses.IncomeTransfer)
        cat_IncomeTransfer.addPartialMatch("transfer from", tranactionClasses.IncomeTransfer)
        cat_IncomeTransfer.addPartialMatch("payment from", tranactionClasses.IncomeTransfer)
        self.AllCategories.append(cat_IncomeTransfer)
        
        cat_BankVerification = baseDefinitions(tranactionClasses.Other, tranactionClasses.BankVerification)
        cat_BankVerification.addPartialMatch("acctverify", tranactionClasses.BankVerification)
        self.AllCategories.append(cat_BankVerification)
        
        cat_ExpenseTransfer = baseDefinitions(tranactionClasses.Expense, tranactionClasses.ExpenseTransfer)
        cat_ExpenseTransfer.addPartialMatch("transfer to", tranactionClasses.ExpenseTransfer)
        cat_ExpenseTransfer.addPartialMatch("payment to", tranactionClasses.ExpenseTransfer)
        self.AllCategories.append(cat_ExpenseTransfer)

        
        print("Classifier initialized")



#class Budget():
#    values = dict()
#    
#    def __init__(self):
#        tclasses = tranactionClasses()
#        tlist = tclasses.returnListOfClasses()
#        
#        
#        ##initialize all values to 0
#        for tclass in tlist:
#            cat = tclass[1]
#            root = tclass[0]
#            self.values[f"{root}-{cat}"] = 0
#            
#    def getBudgetForCategory(self, cat, root):
#        return self.values[f"{root}-{cat}"]
#    
#    def setBudgetForCategory(self, cat, root, value):
#        self.values[f"{root}-{cat}"] = value
#        return
#    
#    def getAllOfKey(self, keyInput="Income"):
#        if self.values is None:
#            return None
#        total = 0
#        for key in self.values:
#            if keyInput in key:
#                total += self.values[key]
#        return total
#    
#    def getAllSummedNonIncome(self):
#        if self.values is None:
#            return None
#        
#        total = 0
#        for key in self.values:
#            if "Income" not in key:
#                total += self.values[key]
#        return total
#    
#    def getAllSummed(self):
#        if self.values is None:
#            return None
#        
#        total = 0
#        for key in self.values:
#            total += self.values[key]
#        return total
#    
#    def getTableData(self):
#        dataplot1x = []
#        dataplot1y = [] #expense root pie
#        data1 = dict()
#        dataplot2x = []
#        dataplot2y = [] #expense category pie
#        data2 = dict()
#        dataplot3x = []
#        dataplot3y = [] #income category pie
#        #dataplot4x = []
#        #dataplot4y = [] #actual ex
#        data3 = dict()
#        #data4 = dict()
#        #x is root category, y is value of root category
#        for i in self.values:
#            root = i.split("-")[0].strip()
#            cat = root
#            if len(i.split("-")) > 1:
#                cat = i.split("-")[1].strip()
#            val = float(self.values[i])
#            if val == 0:
#                continue
#            if root not in data1 and i.isExpense == True:
#                data1[root] = val
#            elif i.isIncome == True:
#                data1[root] += val
#        #convert data1 to list
#        data1 = list(data1.items())
#                
#        #remove all but top 10
#        data1.sort(key=lambda x: x[1], reverse=True)
#        for i in range(0, 9):
#            if i >= len(data1):
#                break
#            dataplot1x.append(data1[i][0])
#            dataplot1y.append(data1[i][1])
#            
#        #category plot
#        for i in self.values:
#            root = i.split("-")[0].strip()
#            cat = root
#            if len(i.split("-")) > 1:
#                cat = i.split("-")[1].strip()
#            val = float(self.values[i])
#            if val == 0:
#                continue
#            if cat not in data2 and i.isExpense == True:
#                data2[cat] = val
#            elif cat in data2 and i.isExpense == True:
#                data2[cat] += val
#            elif cat not in data3 and i.isIncome == True:
#                data3[cat] = val
#            elif cat in data3 and i.isIncome == True:
#                data3[cat] += val
#                
#                
#                
#        #convert data2 to list
#        data2 = list(data2.items())
#                
#        #remove all but top 10
#        data2.sort(key=lambda x: x[1], reverse=True)
#        for i in range(0, 9):
#            if i >= len(data2):
#                break
#            dataplot2x.append(data2[i][0])
#            dataplot2y.append(data2[i][1])
#        print(data3)    
#        #convert data3 to list
#        data3 = list(data3.items())
#        data3.sort(key=lambda x: x[1], reverse=True)
#        for i in range(0, 9):
#            if i >= len(data3):
#                break
#            dataplot3x.append(data3[i][0])
#            dataplot3y.append(data3[i][1])
#        
#            
#        return dataplot1x, dataplot1y, dataplot2x, dataplot2y, dataplot3x, dataplot3y
    
                
class BudgetSet():
    values = dict()
    categories = dict()
    
    def __init__(self, categories=list()):
        self.categories = categories
        self.createEmptyBudget()
        
    def createEmptyBudget(self):
        for cat in self.categories:
            catstr = cat.cat
            rootstr = cat.root
            #print(f"Enter budget for {catstr} in {rootstr}: ")
            key = f"{rootstr}-{catstr}"
            self.values[key] = 0
            
    def getBudgetForCategory(self, cat, root):
        return self.values[f"{root}-{cat}"]
    
    def setBudgetForCategory(self, cat, root, value):
        self.values[f"{root}-{cat}"] = value
        return
    
    def getAllOfKey(self, keyInput="Income"):
        if self.values is None:
            return None
        total = 0
        for key in self.values:
            if keyInput in key:
                total += self.values[key]
        return total
    
    def getAllSummedNonIncome(self):
        if self.values is None:
            return None
        
        #get (root=cat) pairs for all expenses
        rcp = dict()
        for key in self.categories:
            if key.isExpense == True:
                rcp[key.root] = key.cat
        print(rcp)        
        #sum all expenses
        
        
        total = 0
        for key in self.values:
            cat = key.split("-")[1].strip()
            root = key.split("-")[0].strip()
            amt = self.values[key]
            if root in rcp and amt != 0:
                print(f"adding {key} to total for expense (+{self.values[key]})")
                total += self.values[key]
        print(f"total: {total}")
        return round(total, 2)
    
    def getAllSummedIncome(self):
        if self.values is None:
            return None
        
        #get (root=cat) pairs for all expenses
        rcp = dict()
        for key in self.categories:
            if key.isIncome == True:
                rcp[key.root] = key.cat
        #print(rcp)        
        #sum all income
        
        
        total = 0
        for key in self.values:
            cat = key.split("-")[1].strip()
            root = key.split("-")[0].strip()
            
            if root in rcp:
                #print(f"adding {key} to total for income (+{self.values[key]})")
                total += self.values[key]
        return round(total, 2)
    

    
    def getAllSummed(self):
        if self.values is None:
            return None
        
        total = 0
        for key in self.values:
            total += self.values[key]
        return total
    
    def getTableData(self):
        dataplot1x = []
        dataplot1y = [] #expense root pie
        data1 = dict()
        dataplot2x = []
        dataplot2y = [] #expense category pie
        data2 = dict()
        dataplot3x = []
        dataplot3y = [] #income category pie
        #dataplot4x = []
        #dataplot4y = [] #actual ex
        data3 = dict()
        #data4 = dict()
        #x is root category, y is value of root category
        for i in self.values:
            root = i.split("-")[0].strip()
            cat = root
            if len(i.split("-")) > 1:
                cat = i.split("-")[1].strip()
            val = float(self.values[i])
            if val == 0:
                continue
            if root not in data1 and root != "Income":
                data1[root] = val
            elif root != "Income":
                data1[root] += val
        #convert data1 to list
        data1 = list(data1.items())
                
        #remove all but top 10
        data1.sort(key=lambda x: x[1], reverse=True)
        for i in range(0, 9):
            if i >= len(data1):
                break
            dataplot1x.append(data1[i][0])
            dataplot1y.append(data1[i][1])
            
        #category plot
        for i in self.values:
            root = i.split("-")[0].strip()
            cat = root
            if len(i.split("-")) > 1:
                cat = i.split("-")[1].strip()
            val = float(self.values[i])
            if val == 0:
                continue
            if cat not in data2 and root != "Income":
                data2[cat] = val
            elif cat in data2 and root != "Income":
                data2[cat] += val
            elif cat not in data3 and root == "Income":
                data3[cat] = val
            elif cat in data3 and root == "Income":
                data3[cat] += val
                
                
                
        #convert data2 to list
        data2 = list(data2.items())
                
        #remove all but top 10
        data2.sort(key=lambda x: x[1], reverse=True)
        for i in range(0, 9):
            if i >= len(data2):
                break
            dataplot2x.append(data2[i][0])
            dataplot2y.append(data2[i][1])
        print(data3)    
        #convert data3 to list
        data3 = list(data3.items())
        data3.sort(key=lambda x: x[1], reverse=True)
        for i in range(0, 9):
            if i >= len(data3):
                break
            dataplot3x.append(data3[i][0])
            dataplot3y.append(data3[i][1])
        
            
        return dataplot1x, dataplot1y, dataplot2x, dataplot2y, dataplot3x, dataplot3y
    
    def getListOfCategoriesKeys(self):
        cats = list()
        for cat in self.categories:
            catstr = cat.cat
            rootstr = cat.root
            if cat.isRoot == False:
                cats.append(f"{rootstr}-{catstr}")
        return cats
    
    def getListOfCategoriesKeysWithType(self):
        cats = list()
        for cat in self.categories:
            catstr = cat.cat
            rootstr = cat.root
            typeofcat = ""
            
                
            if cat.isRoot == False:
                
                if cat.isExpense == True:
                    typeofcat = "expense"
                elif cat.isIncome == True:
                    typeofcat = "income"
                else:
                    typeofcat = "neutral"
                cats.append((typeofcat,f"{rootstr}-{catstr}"))
                continue
        return cats
    
    def reconcileChangedBudgetFile(self, budgetPath):
        #get all categories, removing categories that are in the budget file but not in the categories file
        #and adding categories that are in the categories file but not in the budget file
        allcatkeys = self.getListOfCategoriesKeys()
        allbudgetkeys = list(self.values.keys())
        #if in categories but not in budget, add to budget
        for cat in allcatkeys:
            if cat not in allbudgetkeys:
                self.values[cat] = 0
        #write updated budget file
        with open(budgetPath, 'w') as json_file:
                json.dump(self.values, json_file)
                json_file.close()
        
        
  
        
    
if __name__ == "__main__":   
    matchstring = "transfer from"

    classifier = Classifier()
    print(classifier.ClassifyDescription(matchstring))
