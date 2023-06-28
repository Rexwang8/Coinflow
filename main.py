
import datetime
import json
from math import ceil, sqrt
import math
import os
from random import Random
import shutil
import dearpygui.dearpygui as dpg
import clipboard

import cfparse
import cfstructs as cfs
import cfclassifier as cfc
import cfstocks

# region classes
class ConfigSettings():
    AppName = "Coinflow"
    ShowFPS = True
    ShowCloseButton = False
    w = 1200
    h = 800
    FontScale = 1.1
    
    isFullScreen = False
    
    l2transactionAmount = 100
    l3transactionAmount = 1000
    currentDefaultUser = ''
    currentDefaultAccount = ''
    dataFolderName = 'data'
    configFileName = 'config.json'
    backupFolderName = 'backup'
    rulesFileName = 'rules.txt'
    categoriesFileName = 'categories.txt'
    stocksFileName = 'stocks.txt'
    
class WindowHandler():
    windows = dict()
    winidx = 0
    
    def addWindow(self, name, pos):
        self.winidx += 1
        uniqueName = f"{name}_{pos}_{self.winidx}"
        self.windows[uniqueName] = self.winidx
        
        
        
    def listWindows(self):
        for key in self.windows:
            print(f"{key} : {self.windows[key]}")
            
    def getTagForId(self, id):
        for key in self.windows:
            if self.windows[key] == id:
                return key
        return None
    
    def printWindows(self):
        print(self.windows)
        
    def getTagForLastWindow(self):
        for key in self.windows:
            if self.windows[key] == self.winidx:
                return key
    
    def __init__(self):
        self.windows = dict()
   
   

class ValueRegistry():
    values = dict()
    
    def addValue(self, name, value):
        self.values[name] = value
        
    def getValue(self, name):
        try:
            return self.values[name]
        except:
            print(f"[Coinflow] ValueRegistry.getValue: {name} not found")
            return None
    
    def __init__(self):
        self.values = dict()    
        
    
    def setValueCB(self, sender, app_data, user_data):
        tag = user_data[0]
        data = user_data[1]
        
        self.addValue(tag, data)
        
    def setInputCB(self, sender, app_data, user_data):
        tag = user_data
        self.addValue(tag, dpg.get_value(sender))
    
class DataHandler():
    users : cfparse.UserManifest = None
    currentuser : cfparse.User = None
    
    #global vals
    createUserName : str = ''
    createAccountName : str = ''
    createAccountType : cfparse.AccountType = cfparse.AccountType.Checking
    runningBalanceSearch : str = ''
    createAccountAmount : float = 0.0
    
    def __init__(self):
        self.users, programDefaultConfig = cfparse.newParse()
        #print(f"type: {type(programDefaultConfig)}")
        #cfg = programDefaultConfig
         
        
        cfg.w = programDefaultConfig.defaultWindow_w
        cfg.h = programDefaultConfig.defaultWindow_h
        if programDefaultConfig.defaultIsFullScreen:
            cb_ChangeFullscreen()
            
        try:
            self.currentuser = self.users.getUserByName(programDefaultConfig.defaultUser)
            assert self.currentuser != None
        except:
            print(f"[Coinflow] Error loading user: {programDefaultConfig.defaultUser}")
            self.currentuser = self.users.users[0]
        print(f"[Coinflow] Loaded User: {self.currentuser.name}")
            
        
        try:
            self.currentuser.currentAccount = self.currentuser.getAccountByName(programDefaultConfig.defaultAccount)
            assert self.currentuser.currentAccount != None
        except:
            print(f"[Coinflow] Error loading account: {programDefaultConfig.defaultAccount}")
            self.currentuser.currentAccount = self.currentuser.accounts[0]
            
        cfg.l2transactionAmount = programDefaultConfig.defaultL2TransactionAmount
        #print(programDefaultConfig.__dict__) 
        cfg.l3transactionAmount = programDefaultConfig.defaultL3TransactionAmount
        cfg.currentDefaultAccount = programDefaultConfig.defaultAccount
        cfg.currentDefaultUser = programDefaultConfig.defaultUser
            
        print(f"[Coinflow] Loaded Account: {self.currentuser.currentAccount.nameOfAccount}")
                
                
                
        
    def setGlobalCreateUserName(self, sender):
        self.createUserName = dpg.get_value(sender)
        
    def setGlobalCreateAccountName(self, sender):
        self.createAccountName = dpg.get_value(sender)
        
    def setGlobalCreateAccountAmount(self, sender):
        self.createAccountAmount = dpg.get_value(sender)
        
    def setGlobalCreateAccountType(self, type):
        self.createAccountType = cfparse.AccountType.parseAccountType(type)
    
    def setGlobalRunningBalanceSearch(self, sender):
        self.runningBalanceSearch = dpg.get_value(sender)
        
        
    def createNewUserFolders(self, name):
        #create user folder
        if not os.path.exists(f"{cfg.dataFolderName}/{name}"):
            os.mkdir(f"{cfg.dataFolderName}/{name}")
        
    def createNewAccountFolders(self, user, account):
        #create account folder
        if not os.path.exists(f"{cfg.dataFolderName}/{user}/{account}"):
            os.mkdir(f"{cfg.dataFolderName}/{user}/{account}")
            
    def createNewUserConfig(self, name, config : cfs.usrconfigjson):
        #create user config file
        with open(f"{cfg.dataFolderName}/{name}/{cfg.configFileName}", "w") as f:
            f.write(json.dumps(cfg.__dict__))
            f.close()
            
    def createNewAccountConfig(self, user, account, config : cfs.acconfigjson):
        #create account config file
        with open(f"{cfg.dataFolderName}/{user}/{account}/{cfg.configFileName}", "w") as f:
            f.write(json.dumps(config.__dict__))
            f.close()
            
    def createNewProgramConfig(self, config : cfs.pgrmconfigjson):
        #create program config file
        with open(f"{cfg.configFileName}", "w") as f:
            f.write(json.dumps(config.__dict__))
            f.close()
                
# endregion                
 
 
# region test callbacks
    
def button_callback(sender, app_data, user_data):
    print(f"sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is: {user_data}")   
    
def notImplementedWindow(sender, app_data, user_data):
    cfs.Logger().log(f"Window not implemented: {app_data}", "DEBUG")
    wh.addWindow("Transactions", (100, 100))
    wtag = wh.getTagForLastWindow()
    
    with dpg.window(label="Not Implemented", tag=wtag, pos=(100, 100), width=300, height=100):
        dpg.add_text("This window is not implemented yet.")
        dpg.add_text("Please check back later.")
        dpg.add_text("Thank you for your support!")
        dpg.add_button(label="Close", callback=cb_CloseWindow, user_data=wtag)
        
    #set window to be modal
    dpg.configure_item(wtag, modal=True)
    #resize window to fit contents
    #set window size
    dpg.set_item_width(wtag, 0.3 * cfg.w)
    dpg.set_item_height(wtag, 0.3 * cfg.h)
    #set window position
    dpg.set_item_pos(wtag, (0.3 * cfg.w, 0.3 * cfg.h))

def print_me(sender):
    print(f"Menu Item: {sender}")
    
def getColorCallback(sender, app_data):
    color = dpg.get_value(sender)
    print(color)
      
def print_value(sender):
    print(dpg.get_value(sender))

    
def change_text(sender, app_data):
    dpg.set_value("text item", f"Mouse Button ID: {app_data}")

#endregion    
    
#region Menu Callbacks

def regenerateMenuUsers():
    #delete all menu items in g_menu_users
    num = len(dpg.get_item_children(g_menu_users).values())
    for idx in range(0, num):
        child = dpg.get_item_children(g_menu_users)[idx]
        for c in child:
            dpg.delete_item(c)
        
    #get name of current user to add checkmark
    cusername = dh.currentuser.name
    
    for user in dh.users.users:
        if user.name == cusername:
            dpg.add_menu_item(label=user.name, callback=cb_ChangeUser, user_data=user.name, parent=g_menu_users, check=True, default_value=True)
        else:
            dpg.add_menu_item(label=user.name, callback=cb_ChangeUser, user_data=user.name, parent=g_menu_users, check=True, default_value=False)
    
def regenerateMenuAccounts():
    #delete all menu items in g_menu_accounts
    num = len(dpg.get_item_children(g_menu_accounts).values())
    for idx in range(0, num):
        child = dpg.get_item_children(g_menu_accounts)[idx]
        for c in child:
            dpg.delete_item(c)
        
    
    #get name of current account to add checkmark
    caccname = dh.currentuser.currentAccount.nameOfAccount

    for account in dh.currentuser.accounts:
        if account.nameOfAccount == caccname:
            dpg.add_menu_item(label=account.nameOfAccount, callback=cb_ChangeAccount, user_data=account.nameOfAccount, parent=g_menu_accounts, check=True, default_value=True)
        else:
            dpg.add_menu_item(label=account.nameOfAccount, callback=cb_ChangeAccount, user_data=account.nameOfAccount, parent=g_menu_accounts, check=True, default_value=False)
 
def cb_ChangeUser(sender, app_data, user_data):
    dh.currentuser = dh.users.getUserByName(user_data)
    dh.currentuser.currentAccount = dh.currentuser.accounts[0]
    
    regenerateMenuUsers()
    regenerateMenuAccounts()
    
def cb_ChangeAccount(sender, app_data, user_data):
    dh.currentuser.currentAccount = dh.currentuser.getAccountByName(user_data)
    
    regenerateMenuUsers()
    regenerateMenuAccounts()    

def cb_callDebugWindow(sender, app_data, user_data):
    if user_data == "debug":
        print("[Coinflow] Debug window called")
        dpg.show_debug()
    elif user_data == "item_registry":
        print("[Coinflow] Item registry called")
        dpg.show_item_registry()
    elif user_data == "show_about":
        print("[Coinflow] About called")
        dpg.show_about()
    elif user_data == "show_metrics":
        print("[Coinflow] Metrics called")
        dpg.show_metrics()
    elif user_data == "show_documentation":
        print("[Coinflow] Documentation called")
        dpg.show_documentation()
    elif user_data == "show_style_editor":
        print("[Coinflow] Style editor called")
        dpg.show_style_editor()
    elif user_data == "show_font_manager":
        print("[Coinflow] Font manager called")
        dpg.show_font_manager()
    
def cb_ChangeFullscreen(sender, app_data, user_data):
    #change fullscreen toggle
    dpg.toggle_viewport_fullscreen()
    if cfg.isFullScreen:
        cfg.isFullScreen = False
    else:
        cfg.isFullScreen = True
 
#endregion 
  
#region Tranactions Window Callbacks
def cb_filterTableTransactions(sender, app_data, user_data):
    tableTag = f"{user_data[0]}"
    filterTag = f"{tableTag}_filter"
    acc = user_data[1]
    isExclude = False
    filterPosOnly = False
    filterNegOnly = False
    filterValue = vr.getValue(user_data[0] + '_filter')
    #classify settings    
    if filterValue.startswith('+'):
        filterPosOnly = True
        filterValue = filterValue[1:]

    if filterValue.startswith('-'):
        filterNegOnly = True
        filterValue = filterValue[1:]
        
    if filterValue.endswith('-'):
        isExclude = True
        filterValue = filterValue[:-1]
        
    def cb_filterTable_Include(filterValue, date, name, amt, type, cat):
        if filterValue in str(name).lower() or filterValue in str(cat).lower() or filterValue in str(type).lower():
            
            return True
        else:
            return False
    
    def cb_filterTable_PosOnly(filterValue, date, name, amt, type, cat):
        if float(amt) > 0:
            return True
        else:
            return False
        
    #remove all rows
    dpg.delete_item(tableTag, children_only=True, slot=1)
    length = len(acc.transactionsByDate)
    print(f"[Coinflow] Filter Specs: {filterValue}, isExclude: {isExclude}, filterPosOnly: {filterPosOnly}")
    row = 0
    for i in range(0, length):
        cell_idx = i
        cell_date = acc.transactionsByDate[i].Date
        cell_desc = acc.transactionsByDate[i].Description
        cell_amt = acc.transactionsByDate[i].Amount
        cell_type = acc.transactionsByDate[i].CreditOrDebit
        cell_labeltype = acc.transactionsByDate[i].labelledType
        cell_acc = acc.nameOfAccount
        cell_root = acc.transactionsByDate[i].AssumedCategory[0]
        cell_cat = acc.transactionsByDate[i].AssumedCategory[1]
        cell_catStr = f"{cell_root} > {cell_cat}"
        cell_catType = acc.transactionsByDate[i].AssumedCategoryType
        if cell_cat == '':
            cell_cat = "Uncategorized"
        if cell_cat == '':
            cell_cat = "Uncategorized"
            
        if not isExclude and filterValue != '':
            if cb_filterTable_Include(filterValue, cell_date, cell_desc, cell_amt, cell_type, cell_cat):
                pass
            else:
                continue
        elif isExclude and filterValue != '':
            if cb_filterTable_Include(filterValue, cell_date, cell_desc, cell_amt, cell_type, cell_cat):
                continue
            else:
                pass
        
        
        if filterPosOnly and filterValue != '':
            if cb_filterTable_PosOnly(filterValue, cell_date, cell_desc, cell_amt, cell_type, cell_cat):
                IncludeRow = True
            else:
                continue
            
        if filterNegOnly and filterValue != '':
            if not cb_filterTable_PosOnly(filterValue, cell_date, cell_desc, cell_amt, cell_type, cell_cat):
                IncludeRow = True
            else:
                continue
            
        with dpg.table_row(parent=tableTag):
            for j in range(0, 7):
                if j == 0:
                    dpg.add_text(f"{cell_idx}")
                elif j == 1:
                    dpg.add_text(f"{cell_date}")
                elif j == 2:
                    #dpg.add_text(f"{cell_desc}")
                    dpg.add_input_text(readonly=True, default_value=cell_desc, width=-1)
                elif j == 3:
                    dpg.add_text(f"{cell_amt}")
                    #set color of text based on withdrawal or deposit
                    dpg_highlight_table_cell(tableTag, cell_amt, row, j)
                        
                elif j == 4:
                    dpg.add_text(f"{cell_type}")
                elif j == 5:
                    dpg.add_text(f"{cell_acc}")
                elif j == 6:
                    dpg.add_text(f"{cell_cat}")
                    if 'income' in str(cell_cat).lower():
                        dpg.highlight_table_cell(tableTag, row, j, (0, 70, 0, 255))
                    elif 'expense' in str(cell_cat).lower():
                        dpg.highlight_table_cell(tableTag, row, j, (70, 0, 0, 255))
            row += 1


def cb_CreateTranactionsWindow(sender, app_data):
    wh.addWindow("Transactions", (100, 100))
    wtag = wh.getTagForId(wh.winidx)
    #wh.listWindows()
    
    winuser = dh.currentuser
    winacc = dh.currentuser.currentAccount
    
    #print(winacc.transactionsByDate)

    with dpg.window(label="Transactions", pos=(100, 100), tag=wtag):
        #move window down and right 5%
        dpg.set_item_pos(wtag, (0.05 * cfg.w, 0.5 * cfg.h))
        dpg.add_text(f"Tranactions from User: {winuser.name}, Account: {winacc.nameOfAccount}")
        #display list of all users and accounts
        tableTag = f"{wtag}_table"
        with dpg.group(horizontal=True):
            inputtxt = dpg.add_input_text(label="Filter (inc, exc-, +pos, -neg)", tag=tableTag + "_filter", callback=vr.setInputCB, user_data=tableTag + "_filter")
            with dpg.item_handler_registry() as registry:
                dpg.add_item_clicked_handler(button=dpg.mvMouseButton_Right, callback=right_click_context_menu, user_data=inputtxt)
                dpg.bind_item_handler_registry(inputtxt, registry)
            
            dpg.add_button(label="Refresh", callback=cb_filterTableTransactions, user_data=(tableTag, winacc))
        dpg.add_separator()
        
        with dpg.table(header_row=True, row_background=True,
                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                   borders_outerV=True, sortable=True, callback=cb_tablesort, tag=tableTag):

            # use add_table_column to add columns to the table,
            # table columns use child slot 0
            dpg.add_table_column(label="Index", width_stretch=True, init_width_or_weight=0.4)
            dpg.add_table_column(label="Date", width_stretch=True, init_width_or_weight=0.8)
            dpg.add_table_column(label="Description", width_stretch=True, init_width_or_weight=2.2)
            dpg.add_table_column(label="Amount", width_stretch=True, init_width_or_weight=1.0)
            dpg.add_table_column(label="Type", width_stretch=True, init_width_or_weight=0.6)
            dpg.add_table_column(label="Label", width_stretch=True, init_width_or_weight=1.0)
            dpg.add_table_column(label="Category", width_stretch=True, init_width_or_weight=2.0)
            
            #set userdata of table to be id of last column
            dpg.set_item_user_data(tableTag, dpg.last_item())
            
            
            # add_table_next_column will jump to the next row
            # once it reaches the end of the columns
            # table next column use slot 1
            
            length = len(winacc.transactionsByDate)
                        
                        
            for i in range(0, length):
                cell_idx = i
                cell_date = winacc.transactionsByDate[i].Date
                cell_desc = winacc.transactionsByDate[i].Description
                cell_amt = winacc.transactionsByDate[i].Amount
                cell_type = winacc.transactionsByDate[i].CreditOrDebit
                cell_labeltype = winacc.transactionsByDate[i].labelledType
                cell_acc = winacc.nameOfAccount
                cell_root = winacc.transactionsByDate[i].AssumedCategory[0]
                cell_cat = winacc.transactionsByDate[i].AssumedCategory[1]
                cell_catStr = f"{cell_root} > {cell_cat}"
                cell_catType = winacc.transactionsByDate[i].AssumedCategoryType
                if cell_cat == '':
                    cell_cat = "Uncategorized"
                with dpg.table_row():
                    for j in range(0, 7):
                        if j == 0:
                            dpg.add_text(f"{cell_idx}")
                        elif j == 1:
                            dpg.add_text(f"{cell_date}")
                            #dpg.add_input_text(readonly=True, default_value=cell_date, width=-1)
                        elif j == 2:
                            #dpg.add_text(f"{cell_desc}")
                            dpg.add_input_text(readonly=True, default_value=cell_desc, width=-1)
                        elif j == 3:
                            dpg.add_text(f"{cell_amt}")
                            #set color of text based on withdrawal or deposit
                            dpg_highlight_table_cell(tableTag, cell_amt, i, j)
                                
                        elif j == 4:
                            dpg.add_text(f"{cell_type}")
                        elif j == 5:
                            dpg.add_text(f"{cell_labeltype}")
                        elif j == 6:
                            dpg.add_text(f"{cell_catStr}")
                            if 'income' in str(cell_catType).lower():
                                dpg.highlight_table_cell(tableTag, i, j, (0, 70, 0, 255))
                            elif 'expense' in str(cell_catType).lower():
                                dpg.highlight_table_cell(tableTag, i, j, (70, 0, 0, 255))
                            elif 'neutral' in str(cell_catType).lower():
                                dpg.highlight_table_cell(tableTag, i, j, (0, 0, 70, 255))
                            
        #set window to be the same size as the table
        #get window item id
        
        #set window size
        dpg.set_item_width(wtag, 0.9 * cfg.w)
        dpg.set_item_height(wtag, 0.9 * cfg.h)
        #set window position
        dpg.set_item_pos(wtag, (0.05 * cfg.w, 0.05 * cfg.h))

#endregion


#region Running Balance Window Callbacks   

def cb_filterTable(sender, app_data, user_data):
    #get table tag
    tableTag = user_data[0]
    acc = user_data[1]
    filterValue = dh.runningBalanceSearch.lower()
    isExclude = False
    filterPosOnly = False
    filterNegOnly = False
    
    #classify settings    
    if filterValue.startswith('+'):
        filterPosOnly = True
        filterValue = filterValue[1:]

    if filterValue.startswith('-'):
        filterNegOnly = True
        filterValue = filterValue[1:]
        
    if filterValue.endswith('-'):
        isExclude = True
        filterValue = filterValue[:-1]
        
    def cb_filterTable_Include(filterValue, date, name, amt, bal):
        if filterValue in str(name).lower():
            
            return True
        else:
            return False
    
    def cb_filterTable_PosOnly(filterValue, date, name, amt, bal):
        if float(amt) > 0:
            return True
        else:
            return False
    
        
        
        
    #remove all rows from table child[1]
    #dpg.delete_item(tableTag, children_only=True)
    
    dpg.delete_item(tableTag, children_only=True, slot=1)
        
    #add rows back to table
    row = 0
    print(f"[Coinflow] Filter Specs: {filterValue}, isExclude: {isExclude}, filterPosOnly: {filterPosOnly}")
    for i in range(0, len(acc.transactionsByDate)):
        transaction = dh.currentuser.currentAccount.transactionsByDate[i]
        date = transaction.Date
        name = transaction.Description
        amt = transaction.Amount
        bal = transaction.Balance
        IncludeRow = True
        if not isExclude and filterValue != '':
            if cb_filterTable_Include(filterValue, date, name, amt, bal):
                pass
            else:
                continue
        elif isExclude and filterValue != '':
            if cb_filterTable_Include(filterValue, date, name, amt, bal):
                continue
            else:
                pass
        
        
        if filterPosOnly and filterValue != '':
            if cb_filterTable_PosOnly(filterValue, date, name, amt, bal):
                IncludeRow = True
            else:
                continue
            
        if filterNegOnly and filterValue != '':
            if not cb_filterTable_PosOnly(filterValue, date, name, amt, bal):
                IncludeRow = True
            else:
                continue
                

            
        with dpg.table_row(parent=tableTag):
            for j in range(0, 4):
                if j == 0:
                    dpg.add_text(date)
                elif j == 1:
                    dpg.add_text(f"{name}")
                    
                    dpg.unhighlight_table_cell(tableTag, row=row, column=1)
                    if filterValue != '':
                        dpg.highlight_table_cell(tableTag, row, j, (0, 0, 50, 255))
                elif j == 2:
                    dpg.add_text(amt)
                    dpg_highlight_table_cell(tableTag, amt, row, j)
                elif j == 3:
                    dpg.add_text(bal)
        row += 1

                            
 
def cb_CreateRunningBalanceWindow(sender, app_data, user_data):
    wh.addWindow("Running Balance", (100, 100))
    #wh.listWindows()
    wtag = wh.getTagForId(wh.winidx)
    wh.listWindows()
    wh.printWindows()
    print(f"Using tag: {wtag} for window {wh.winidx}")
    wtag = Random().randint(1000, 1000000)

     
    with dpg.window(label='Running Balance', pos=(100,100), tag=wtag):
        #move window down and right 5%
        dpg.add_text(f"Balance from User: {dh.currentuser.name}, Account: {dh.currentuser.currentAccount.nameOfAccount}")
        acctypetxt = dh.currentuser.currentAccount.typeOfAccount
        dpg.add_text(f"Account Type: {acctypetxt}")
        dpg.add_radio_button(("Shaded", "TODO", "TODO"), callback=button_callback, horizontal=True)

        dpg.add_separator()
        ## plot that shows running balance by date
        
        #TODO: add running balance calc for credit instead of fixed balance
        if len(dh.currentuser.currentAccount.transactionsByDate) > 0:
            data = list()
            for i in range(0, len(dh.currentuser.currentAccount.transactionsByDate)):
                transaction = dh.currentuser.currentAccount.transactionsByDate[i]
                d = datetime.datetime.strptime(transaction.Date, "%m/%d/%Y") 
                #convert to unix
                d = datetime.datetime.timestamp(d)
                b = float(transaction.Balance)
                data.append((d, b))


            #for transactions with the same timestamp, add use the biggest balance
            data_dedup = list()
            for i in range(0, len(data)):
                keys = [x[0] for x in data_dedup]
                new_key = data[i][0]
                if new_key not in keys:
                    data_dedup.append(data[i])

            ##sort by date then by balance, decending
            data_dedup.sort(key=lambda x: (x[0], x[1]), reverse=False)
            #sort by balance ascending
            data_dedup.reverse()



            plotX = []
            plotY = []
            for i in range(0, len(data_dedup)):
                plotX.append(data_dedup[i][0])
                plotY.append(data_dedup[i][1])



            with dpg.theme(tag=f"{wtag}_theme1"):
                with dpg.theme_component(0):
                    dpg.add_theme_color(dpg.mvPlotCol_Line, (30, 30, 255), category=dpg.mvThemeCat_Plots)
                    dpg.add_theme_color(dpg.mvPlotCol_Fill, (30, 30, 150, 100), category=dpg.mvThemeCat_Plots)    
            # create plot
            with dpg.plot(label="Line Series", height=400, width=-1):
                dpg.bind_colormap(dpg.last_item(), dpg.mvPlotColormap_Default)
                # optionally create legend
                dpg.add_plot_legend()
                # REQUIRED: create x and y axes
                xaxis = dpg.add_plot_axis(dpg.mvXAxis, label="Days from Latest Date", time=True)
                with dpg.plot_axis(dpg.mvYAxis, label="Amount"):
                    # series belong to a y axis
                    dpg.add_shade_series(plotX, plotY, label="Running Balance by Date")
                    dpg.bind_item_theme(dpg.last_item(), f"{wtag}_theme1")
                dpg.fit_axis_data(xaxis)
            
            
        dpg.add_separator()
        ## table that shows running balance summary
        table1tag = f"{wtag}_table1"
        with dpg.group(horizontal=True):
            itxt = dpg.add_input_text(label="Filter (inc, exc-, +pos, -neg)", tag=table1tag + "_filter", callback=dh.setGlobalRunningBalanceSearch)
            with dpg.item_handler_registry() as registry:
                dpg.add_item_clicked_handler(button=dpg.mvMouseButton_Right, callback=right_click_context_menu, user_data=itxt)
                dpg.bind_item_handler_registry(itxt, registry)
            dpg.add_button(label="Refresh", callback=cb_filterTable, user_data=(table1tag, dh.currentuser.currentAccount))
        with dpg.table(header_row=True, row_background=True,
                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                   borders_outerV=True, sortable=True, callback=cb_tablesort2, tag=table1tag):
            
            dpg.add_table_column(label="Date", width_stretch=True, init_width_or_weight=1.0)
            dpg.add_table_column(label="Name", width_stretch=True, init_width_or_weight=1.0)
            dpg.add_table_column(label="Amount", width_stretch=True, init_width_or_weight=1.0)
            dpg.add_table_column(label="Balance", width_stretch=True, init_width_or_weight=1.0)
            
            #set userdata of table to be id of last column
            dpg.set_item_user_data(table1tag, dpg.last_item())
            
            
            dh.runningBalanceSearch = ''
            cb_filterTable(None, None, (table1tag, dh.currentuser.currentAccount))
                            

                    
                    
        dpg.add_separator()
        
        
        
        
        
    #set window to be large enough to fit the table
    dpg.set_item_width(wtag, 0.9 * cfg.w)
    dpg.set_item_height(wtag, 0.9 * cfg.h)
    dpg.set_item_pos(wtag, (0.05 * cfg.w, 0.05 * cfg.h))
    
    
def cb_tablesort2(sender, app_data):
    # sort_specs scenarios:
    #   1. no sorting -> sort_specs == None
    #   2. single sorting -> sort_specs == [[column_id, direction]]
    #   3. multi sorting -> sort_specs == [[column_id, direction], [column_id, direction], ...]
    #
    # notes:
    #   1. direction is ascending if == 1
    #   2. direction is ascending if == -1

    # no sorting case
    if app_data is None: return

    rows = dpg.get_item_children(sender, 1)

    # create a list that can be sorted based on first cell
    # value, keeping track of row and value used to sort
    sortable_list = []
    
    lastid = dpg.get_item_user_data(sender)
    firstid = lastid - 3
    rawid = app_data[0][0]
    colid = rawid - firstid
    

    for row in rows:
        if dpg.get_item_children(row, 1) == []:
            continue
        date = dpg.get_item_children(row, 1)[0]
        name = dpg.get_item_children(row, 1)[1]
        amt = dpg.get_item_children(row, 1)[2]
        bal = dpg.get_item_children(row, 1)[3]
        if colid == 0:
            dateasunix = datetime.datetime.strptime(dpg.get_value(date), '%m/%d/%Y').timestamp()
            sortable_list.append((row, dateasunix, dpg.get_value(bal)))
        elif colid == 1:
            sortable_list.append((row, dpg.get_value(name)))
        elif colid == 2:
            sortable_list.append((row, dpg.get_value(amt)))
        elif colid == 3:
            sortable_list.append((row, dpg.get_value(bal)))

    def _sorter(e):
        return e[1]
    
    def _sorterDate(e):
        return e[1], e[2]
    
    if colid == 2:
        for i in range(len(sortable_list)):
            sortable_list[i] = (sortable_list[i][0], float(sortable_list[i][1]))

    if colid != 0:
        sortable_list.sort(key=_sorter, reverse=app_data[0][1] < 0)
    else:
        sortable_list.sort(key=_sorterDate, reverse=app_data[0][1] < 0)

    # create list of just sorted row ids
    new_order = []
    for pair in sortable_list:
        new_order.append(pair[0])

    dpg.reorder_items(sender, 1, new_order)

def dpg_highlight_table_cell(table, amt, row, column, mul=1):
    #consts for colors
    BrightRed = (200, 0, 0, 255)
    BrightGreen = (0, 200, 0, 255)
    Red = (110, 0, 0, 255)
    Green = (0, 110, 0, 255)
    DarkRed = (50, 0, 0, 255)
    DarkGreen = (0, 50, 0, 255)

    if amt > 0:
        if amt >= cfg.l3transactionAmount * mul:
            dpg.highlight_table_cell(table, row, column, BrightGreen)
        elif amt >= cfg.l2transactionAmount * mul:
            dpg.highlight_table_cell(table, row, column, Green)
        else:
            dpg.highlight_table_cell(table, row, column, DarkGreen)
            
    elif amt < 0:
        if amt <= -cfg.l3transactionAmount * mul:
            dpg.highlight_table_cell(table, row, column, BrightRed)
        elif amt <= -cfg.l2transactionAmount * mul:
            dpg.highlight_table_cell(table, row, column, Red)
        else:
            dpg.highlight_table_cell(table, row, column, DarkRed)

#endregion

#region User Window Callbacks

def cb_CancelCreateUser(sender, app_data, user_data):
    
    dh.createUserName = ""
    cb_DeleteWindow(sender, app_data, user_data)
    
def cb_CreateUserWindow(sender, app_data):
    #create window
    wh.addWindow("Create User", (100, 100))
    wh.listWindows()
    
    wtag = wh.getTagForId(wh.winidx)
    
    with dpg.window(label="Create User", pos=(100, 100), tag=wtag, width=600, height=500):
        dpg.add_text(f"Create a new user")
        txtinput = dpg.add_input_text(label="Enter Name", hint="Name", no_spaces=True)
        with dpg.item_handler_registry() as registry:
            dpg.add_item_clicked_handler(button=dpg.mvMouseButton_Right, callback=right_click_context_menu, user_data=txtinput)
            dpg.bind_item_handler_registry(txtinput, registry)
        #get previous input text item from id
        dpg.set_item_callback(txtinput, dh.setGlobalCreateUserName)

        btn1 = dpg.add_button(label="Create User", callback=cb_CreateUser)
        dpg.set_item_user_data(btn1, wtag)
        #dpg.set_item_user_data("btn1", "Some Extra User Data")
        btn2 = dpg.add_button(label="Cancel", callback=cb_CancelCreateUser, user_data=None)
        dpg.set_item_user_data(btn2, wtag)
        
        #display current user and account
        dpg.add_text(f"Current User: {dh.currentuser.name}")
        dpg.add_text(f"Current Account: {dh.currentuser.currentAccount.nameOfAccount}")
        
        #display list of all users and accounts
        with dpg.table(header_row=True, row_background=True,
                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                   borders_outerV=True, sortable=True):
            
            dpg.add_table_column(label="User", width_stretch=True, init_width_or_weight=0.0)
            dpg.add_table_column(label="Account", width_stretch=True, init_width_or_weight=0.0)
            dpg.add_table_column(label="Type", width_stretch=True, init_width_or_weight=0.0)
            dpg.add_table_column(label="Count", width_stretch=True, init_width_or_weight=0.0)
                    
                    
            for i in range(0, len(dh.users.users)):
                user = dh.users.users[i]
                username = user.name


                with dpg.table_row():
                        dpg.add_text(f"{username}")
                        dpg.add_text(f"Accounts: -->")
                        dpg.add_text(f"User")
                        dpg.add_text(f"{len(user.accounts)}")

                for j in range(0, len(user.accounts)):
                    acc : cfparse.Account = user.accounts[j]
                    accname = acc.nameOfAccount
                
                    
                    
                    
                    
                    
                    with dpg.table_row():
                        dpg.add_text(f"{username}")
                        dpg.add_text(f"{accname}")
                        dpg.add_text(f"{acc.typeOfAccount}")
                        dpg.add_text(f"{len(acc.transactionsByDate)}")

def cb_CreateUser(sender, app_data, user_data):
    #in user data
    wtag = user_data
    name = dh.createUserName

    if name == "" or name == None:
        dh.createUserName = ""
        return
    
    else:
        name = sanitizeString(name)
        name = "u_" + name
        if name not in dh.users.listOfUsernames:
            #create user
            userid = wrapper_addUser(name)
            
            dh.users.listUsers()
            #exit window
            cb_DeleteWindow(sender, app_data, wtag)
            return
        else:
            print(f"[Coinflow] User: {name} already exists")
            #create popup window
            #create uuid for popup window tag
            uuid = str(dpg.generate_uuid())
            with dpg.window(label="User Exists", pos=(200, 200), tag=uuid, modal=True, show=False):
                dpg.add_text(f"User: {name} already exists")
                #delete button
                dpg.add_button(label="Ok", callback=cb_DeleteWindow, user_data=uuid)
            
            dpg.configure_item(uuid, show=True)    
   
def cb_tablesort(sender, app_data):
    # sort_specs scenarios:
    #   1. no sorting -> sort_specs == None
    #   2. single sorting -> sort_specs == [[column_id, direction]]
    #   3. multi sorting -> sort_specs == [[column_id, direction], [column_id, direction], ...]
    #
    # notes:
    #   1. direction is ascending if == 1
    #   2. direction is ascending if == -1

    # no sorting case
    if app_data is None: return

    rows = dpg.get_item_children(sender, 1)

    # create a list that can be sorted based on first cell
    # value, keeping track of row and value used to sort
    sortable_list = []
    
    lastid = dpg.get_item_user_data(sender)
    firstid = lastid - 6
    rawid = app_data[0][0]
    colid = rawid - firstid
    
    
    for row in rows:
        idx = dpg.get_item_children(row, 1)[0]
        date = dpg.get_item_children(row, 1)[1]
        desc = dpg.get_item_children(row, 1)[2]
        amt = dpg.get_item_children(row, 1)[3]
        ty = dpg.get_item_children(row, 1)[4]
        acc = dpg.get_item_children(row, 1)[5]
        cat = dpg.get_item_children(row, 1)[6]
        if colid == 0:
            sortable_list.append([row, float(dpg.get_value(idx))])
        elif colid == 1:
            datainunix = datetime.datetime.strptime(dpg.get_value(date), "%m/%d/%Y")
            sortable_list.append([row, datainunix])
        elif colid == 2:
            sortable_list.append([row, dpg.get_value(desc)])
        elif colid == 3:
            sortable_list.append([row, float(dpg.get_value(amt))])
        elif colid == 4:
            sortable_list.append([row, dpg.get_value(ty)])
        elif colid == 5:
            sortable_list.append([row, dpg.get_value(acc)])
        elif colid == 6:
            sortable_list.append([row, dpg.get_value(cat)])

    def _sorter(e):
        return e[1]

    sortable_list.sort(key=_sorter, reverse=app_data[0][1] < 0)

    # create list of just sorted row ids
    new_order = []
    for pair in sortable_list:
        new_order.append(pair[0])

    dpg.reorder_items(sender, 1, new_order)

def cb_deleteUserWindow(sender, app_data, user_data):
    print(f"app_data: {app_data}")
    print(f"user_data: {user_data}")
    wh.addWindow("Delete User", (100, 100))
    #wh.listWindows()
    wtag = wh.getTagForId(wh.winidx)
    
    #get context
    winuser = dh.currentuser
    winacc = dh.currentuser.currentAccount
    
    userlist = dh.users
    
    #create window
    with dpg.window(label="Delete User", pos=(100, 100), tag=wtag, width=600, height=500):
        dpg.add_text(f"Delete User")
        
        #list all users
        with dpg.table(header_row=True, reorderable=True, callback=cb_tablesort, user_data=wh.winidx, tag=f"{wtag}_table"):
            dpg.add_table_column(label="Username", width_fixed=True, width=100)
            dpg.add_table_column(label="Accounts", width_fixed=True, width=100)
            dpg.add_table_column(label="Transactions", width_fixed=True, width=100)
            dpg.add_table_column(label="Delete", width_fixed=True, width=100)
            
            for i in range(0, len(dh.users.users)):
                user : cfparse.User = dh.users.users[i]
                username = user.name
                
                with dpg.table_row():
                    dpg.add_text(f"{username}")
                    dpg.add_text(f"{len(user.accounts)}")
                    dpg.add_text(f"{user.countTransactions()}")
                    dpg.add_button(label="Delete", callback=cb_deleteUserConfirm, user_data=(user, f"{wtag}_table"))
                    
        
    #set window size
    dpg.set_item_width(wtag, 0.4 * cfg.w)
    dpg.set_item_height(wtag, 0.4 * cfg.h)
    #set window position
    dpg.set_item_pos(wtag, (0.05 * cfg.w, 0.05 * cfg.h))
        
def cb_deleteUserConfirm(sender, app_data, user_data):
    user = user_data[0]
    tabletag = user_data[1]
    status = ''
    wh.addWindow("Delete User Confirm", (100, 100))
    #wh.listWindows()
    wtag = wh.getTagForId(wh.winidx)
    #check if last user
    if len(dh.users.users) == 1:
        cfs.Logger().log(status, "INFO")
        with dpg.window(label="Cannot Delete Last User", pos=(100, 100), tag=wtag, width=600, height=500, modal=True):
            dpg.add_text(f"Cannot Delete User")
            dpg.add_button(label="Close", callback=cb_CloseWindow, user_data=wtag)
        #set window size
        dpg.set_item_width(wtag, 0.3 * cfg.w)
        dpg.set_item_height(wtag, 0.3 * cfg.h)
        #set window position
        dpg.set_item_pos(wtag, (0.3 * cfg.w, 0.3 * cfg.h))
        return
        
    
    
    with dpg.window(label="Delete User", pos=(100, 100), tag=wtag, width=600, height=500, modal=True):
        dpg.add_text(f"Confirm Delete User: {user.name}")
        with dpg.group(horizontal=True):
            dpg.add_button(label="Cancel", callback=cb_CloseWindow, user_data=wtag)
            dpg.add_button(label="Confirm", callback=cb_deleteUser, user_data=(user, wtag, tabletag))
            
    #set window size
    dpg.set_item_width(wtag, 0.3 * cfg.w)
    dpg.set_item_height(wtag, 0.3 * cfg.h)
    #set window position
    dpg.set_item_pos(wtag, (0.3 * cfg.w, 0.3 * cfg.h))

    
def cb_deleteUser(sender, app_data, user_data):
    user = user_data[0]
    pwtag = user_data[1]
    tabletag = user_data[2]
    wh.addWindow("Delete User Status", (100, 100))
    wtag = wh.getTagForId(wh.winidx)
    status = ''
    cfs.Logger().log(f"Deleting user: {user.name} which has {len(user.accounts)} accounts", "INFO")
    try:
        shutil.rmtree(user.path)
        
        #remove from dh
        dh.users.users.remove(user)
        status = f"User {user.name} deleted successfully"
    except:
        status = f"Failed to delete user {user.name}"
        cfs.Logger().log(status, "ERROR")
        return
    with dpg.window(label="Delete User Status", pos=(100, 100), tag=wtag, width=600, height=500, on_close=cb_CloseMultipleWindows, user_data=(pwtag, wtag)):
        dpg.add_text(f"User Delete Status: \n{status}")
        dpg.add_button(label="Confirm", callback=cb_CloseMultipleWindows, user_data=(pwtag, wtag))
    dh.currentuser = dh.users.users[0]
    dh.currentuser.currentAccount = dh.currentuser.accounts[0]
    #set window size
    dpg.set_item_width(wtag, 0.3 * cfg.w)
    dpg.set_item_height(wtag, 0.3 * cfg.h)
    #set window position
    dpg.set_item_pos(wtag, (0.3 * cfg.w, 0.3 * cfg.h))
    
    #refresh ui
    regenerateMenuAccounts()
    regenerateMenuUsers()
    #refresh table
    dpg.delete_item(tabletag, children_only=True, slot=1)
    for i in range(0, len(dh.users.users)):
        user : cfparse.User = dh.users.users[i]
        username = user.name
        
        with dpg.table_row(parent=tabletag):
            dpg.add_text(f"{username}")
            dpg.add_text(f"{len(user.accounts)}")
            dpg.add_text(f"{user.countTransactions()}")
            dpg.add_button(label="Delete", callback=cb_deleteUserConfirm, user_data=(user, tabletag))
    

#endregion


#region Account Window Callbacks

def cb_createAccount(sender, app_data, user_data):
    #in user data
    wtag = user_data
    name = dh.createAccountName
    acctype = dh.createAccountType
    accsbal = dh.createAccountAmount

    
    #input checks
    if name == "" or name == None:
        dh.createAccountName = ""
        return
    
    if accsbal == "" or accsbal == None:
        accsbal = 0
    
    if acctype == "" or acctype == None or acctype == "<None>" or acctype == "None":
        dh.createAccountType = ""
        return

    
    
    else:
        name = sanitizeString(name)
        name = "a_" + name
        if name not in dh.users.listOfUsernames:
            #create account
            print(f"[Coinflow] Creating account: {name} of type: {acctype} with starting balance: {accsbal}")
            userid = wrapper_addAccount(name, acctype, accsbal)
            
            #exit window
            cb_DeleteWindow(sender, app_data, wtag)
            return
        else:
            print(f"[Coinflow] Account: {name} already exists for user")
            #create popup window
            #create uuid for popup window tag
            uuid = str(dpg.generate_uuid())
            with dpg.window(label="Account Exists", pos=(200, 200), tag=uuid, modal=True, show=False):
                dpg.add_text(f"Account: {name} already exists for user")
                #delete button
                dpg.add_button(label="Ok", callback=cb_DeleteWindow, user_data=uuid)
            
            dpg.configure_item(uuid, show=True)    

def cb_CancelCreateAccount(sender, app_data, user_data):
    dh.createAccountName = ""
    cb_DeleteWindow(sender, app_data, user_data)
    
def cb_deleteAccWindow(sender, app_data, user_data):
    wh.addWindow("Delete Account", (100, 100))
    wtag = wh.getTagForId(wh.winidx)
    
    #get context
    winuser = dh.currentuser
    winacc = dh.currentuser.currentAccount
    
    accList = winuser.accounts
    
    #create window
    with dpg.window(label="Delete Account", pos=(100, 100), tag=wtag, width=600, height=500):
        dpg.add_text(f"Delete Account")
        
        #list all users
        with dpg.table(header_row=True, reorderable=True, callback=cb_tablesort, user_data=wh.winidx, tag=f"{wtag}_table"):
            dpg.add_table_column(label="Account Name", width_fixed=True, width=100)
            dpg.add_table_column(label="Transactions", width_fixed=True, width=100)
            dpg.add_table_column(label="Delete", width_fixed=True, width=100)
            
            for i in range(0, len(accList)):
                acc : cfparse.Account = accList[i]
                accName = acc.nameOfAccount
                
                with dpg.table_row():
                    dpg.add_text(f"{accName}")
                    dpg.add_text(f"{len(acc.transactionsByDate)}")
                    dpg.add_button(label="Delete", callback=cb_deleteAccConfirm, user_data=(acc, f"{wtag}_table"))
                    
        
    #set window size
    dpg.set_item_width(wtag, 0.4 * cfg.w)
    dpg.set_item_height(wtag, 0.4 * cfg.h)
    #set window position
    dpg.set_item_pos(wtag, (0.05 * cfg.w, 0.05 * cfg.h))

def cb_deleteAccConfirm(sender, app_data, user_data):
    acc = user_data[0]
    tabletag = user_data[1]
    status = ''
    wh.addWindow("Delete Account Confirm", (100, 100))
    #wh.listWindows()
    wtag = wh.getTagForId(wh.winidx)
    #check if last user
    if len(dh.currentuser.accounts) == 1:
        cfs.Logger().log(status, "INFO")
        with dpg.window(label="Cannot Delete Last Account", pos=(100, 100), tag=wtag, width=600, height=500, modal=True):
            dpg.add_text(f"Cannot Delete Account")
            dpg.add_button(label="Close", callback=cb_CloseWindow, user_data=wtag)
        #set window size
        dpg.set_item_width(wtag, 0.3 * cfg.w)
        dpg.set_item_height(wtag, 0.3 * cfg.h)
        #set window position
        dpg.set_item_pos(wtag, (0.3 * cfg.w, 0.3 * cfg.h))
        return
        
    
    
    with dpg.window(label="Delete Account", pos=(100, 100), tag=wtag, width=600, height=500, modal=True):
        dpg.add_text(f"Confirm Delete Account: {acc.nameOfAccount}")
        with dpg.group(horizontal=True):
            dpg.add_button(label="Cancel", callback=cb_CloseWindow, user_data=wtag)
            dpg.add_button(label="Confirm", callback=cb_deleteAcc, user_data=(acc, wtag, tabletag))
            
    #set window size
    dpg.set_item_width(wtag, 0.3 * cfg.w)
    dpg.set_item_height(wtag, 0.3 * cfg.h)
    #set window position
    dpg.set_item_pos(wtag, (0.3 * cfg.w, 0.3 * cfg.h))
    
def cb_deleteAcc(sender, app_data, user_data):
    acc = user_data[0]
    pwtag = user_data[1]
    tabletag = user_data[2]
    wh.addWindow("Delete Account Status", (100, 100))
    wtag = wh.getTagForId(wh.winidx)
    status = ''
    cfs.Logger().log(f"Deleting Account: {acc.nameOfAccount}", "INFO")
    try:
        print(f"path: {acc.path}")
        shutil.rmtree(acc.path)
        
        #remove from dh
        dh.currentuser.accounts.remove(acc)
        status = f"Account {acc.nameOfAccount} deleted successfully"
    except:
        status = f"Failed to delete account {acc.nameOfAccount}"
        cfs.Logger().log(status, "ERROR")
        return
    with dpg.window(label="Delete Account Status", pos=(100, 100), tag=wtag, width=600, height=500, on_close=cb_CloseMultipleWindows, user_data=(pwtag, wtag)):
        dpg.add_text(f"Account Delete Status: \n{status}")
        dpg.add_button(label="Confirm", callback=cb_CloseMultipleWindows, user_data=(pwtag, wtag))
    dh.currentuser.currentAccount = dh.currentuser.accounts[0]
    #set window size
    dpg.set_item_width(wtag, 0.3 * cfg.w)
    dpg.set_item_height(wtag, 0.3 * cfg.h)
    #set window position
    dpg.set_item_pos(wtag, (0.3 * cfg.w, 0.3 * cfg.h))
    
    #refresh ui
    regenerateMenuAccounts()
    regenerateMenuUsers()
    #refresh table
    accList = dh.currentuser.accounts
    dpg.delete_item(tabletag, children_only=True, slot=1)
    for i in range(0, len(accList)):
        acc : cfparse.Account = accList[i]
        accName = acc.nameOfAccount

        with dpg.table_row(parent=tabletag):
            dpg.add_text(f"{accName}")
            dpg.add_text(f"{len(acc.transactionsByDate)}")
            dpg.add_button(label="Delete", callback=cb_deleteAccConfirm, user_data=(acc, f"{wtag}_table"))


def wrapper_addAccount(name, atype=cfparse.AccountType.Checking, sbal=0):
    
    account = cfparse.Account(name, sbal, 0, atype)
    account.path = dh.currentuser.path + f"/{name}"
    account.setBalance(sbal)
    uid = dh.currentuser.addAccount(account)
    #switch to account
    dh.currentuser.currentAccount = account
    
    #create new folder for user
    username = dh.currentuser.name
    dh.createNewUserFolders(username)
    dh.createNewAccountFolders(username, name)
    
    acConfig = cfs.acconfigjson(name, str(atype))
    dh.createNewAccountConfig(username, name, acConfig)
    usrConfig = cfs.usrconfigjson(username)
    dh.createNewUserConfig(username, usrConfig)
    
    
    regenerateMenuAccounts()
    regenerateMenuUsers()
    
    return uid

def cb_ChangeAccountTypeUI(sender, app_data, user_data):
    #update text from item id stored in user_data
    dpg.set_value(user_data[0], user_data[1])
    
    #update global
    dh.setGlobalCreateAccountType(user_data[1])

def cb_CreateAccountWindow(sender, app_data, user_data):
    #create window
    wh.addWindow("Create Account", (100, 100))
    #wh.listWindows()
    
    wtag = wh.getTagForId(wh.winidx)
    
    with dpg.window(label="Create Account", pos=(100, 100), tag=wtag, width=600, height=500):
        dpg.add_text(f"Create a new Account")
        txtinput = dpg.add_input_text(label="Enter Account Name", hint="Name", no_spaces=True)
        with dpg.item_handler_registry() as registry:
            dpg.add_item_clicked_handler(button=dpg.mvMouseButton_Right, callback=right_click_context_menu, user_data=txtinput)
            dpg.bind_item_handler_registry(txtinput, registry)
        sbalinput = dpg.add_input_float(label="Enter Starting Balance")
        
        #get previous input text item from id
        dpg.set_item_callback(txtinput, dh.setGlobalCreateAccountName)
        dpg.set_item_callback(sbalinput, dh.setGlobalCreateAccountAmount)

        btn1 = dpg.add_button(label="Create Account", callback=cb_createAccount)
        dpg.set_item_user_data(btn1, wtag)
        #dpg.set_item_user_data("btn1", "Some Extra User Data")
        btn2 = dpg.add_button(label="Cancel", callback=cb_CancelCreateAccount, user_data=None)
        dpg.set_item_user_data(btn2, wtag)
        
        
        #display current user and account
        dpg.add_text(f"Current User: {dh.currentuser.name}")
        dpg.add_text(f"Current Account: {dh.currentuser.currentAccount.nameOfAccount}")
        
        #display type of account
        popup_values = ["Checking", "Savings", "Credit", "Investment", "Cash"]
        with dpg.group(horizontal=True):
            b = dpg.add_button(label="Account Type...")
            t = dpg.add_text("<None>")
            dpg.set_item_user_data(b, t)
            with dpg.popup(b, tag=f"{wtag}_popup", mousebutton=dpg.mvMouseButton_Left, modal=True):
                dpg.add_text("Account Type")
                dpg.add_separator()
                for i in popup_values:
                    dpg.add_selectable(label=i, user_data=[t, i], callback=cb_ChangeAccountTypeUI)
        #add callback to button to set account type
        dpg.add_separator()
        
        #display list of all users and accounts
        with dpg.table(header_row=True, row_background=True,
                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                   borders_outerV=True, sortable=True):
            dpg.add_table_column(label="User", width_stretch=True, init_width_or_weight=0.0)
            dpg.add_table_column(label="Account", width_stretch=True, init_width_or_weight=0.0)
            dpg.add_table_column(label="Type", width_stretch=True, init_width_or_weight=0.0)
            dpg.add_table_column(label="Starting Balance", width_stretch=True, init_width_or_weight=0.0)
            dpg.add_table_column(label="Count", width_stretch=True, init_width_or_weight=0.0)
            
            for i in range(0, len(dh.users.users)):
                user = dh.users.users[i]
                username = user.name


                with dpg.table_row():
                        dpg.add_text(f"{username}")
                        dpg.add_text(f"Accounts: -->")
                        dpg.add_text(f"User")
                        dpg.add_text(f"User")
                        dpg.add_text(f"{len(user.accounts)}")

                for j in range(0, len(user.accounts)):
                    acc : cfparse.Account = user.accounts[j]
                    accname = acc.nameOfAccount
                
                    
                    

                    
                    with dpg.table_row():
                        dpg.add_text(f"{username}")
                        dpg.add_text(f"{accname}")
                        dpg.add_text(f"{acc.typeOfAccount}")
                        dpg.add_text(f"{acc.balance}")
                        dpg.add_text(f"{len(acc.transactionsByDate)}")
        
#endregion  
  
        
#region Budget Window Callbacks
def cb_CreateBudgetWindow(sender, app_data, user_data):
    #set windows
    wh.addWindow("Create Budget", (100, 100))
    #wh.listWindows()
    wtag = wh.getTagForId(wh.winidx)
    #get context
    winuser = dh.currentuser
    winacc = dh.currentuser.currentAccount
    
    winbudget = winuser.budget
    #print(winbudget)
    #calc values
    btotal = winbudget.getAllSummedNonIncome()
    btotalTag = f"{wtag}_btotal"
    vr.addValue(btotalTag, btotal)
    #print(btotal, vr.getValue(btotalTag))
    
    binc = winbudget.getAllSummedIncome()
    bincTag = f"{wtag}_binc"
    vr.addValue(bincTag, binc)
    
    
    thirtyDay = winuser.getBudgetTransactions(30)
    nintyDay = winuser.getBudgetTransactions(90)
    
    thirtyDaySum = 0
    for i in thirtyDay:
        thirtyDaySum += float(thirtyDay[i])
    nintyDaySum = 0
    for i in nintyDay:
        nintyDaySum += float(nintyDay[i])
    
    thirtyDaySum = round(thirtyDaySum, 2)
    nintyDaySum = round(nintyDaySum, 2)
    
    with dpg.window(label="Budget", pos=(100, 100), tag=wtag, width=600, height=500):
        with dpg.group(horizontal=True):
            dpg.add_text(f"Budgeting Window | ")
            dpg.add_text(f"Current User: {winuser.name}")
            dpg.add_text(f"Current Account: ALL ({len(winuser.accounts)} accounts)")
        dpg.add_separator()
        
        
        
        ## Pie Chart
        dpg.add_text("Budget Breakdown ")
        dpg.add_text("Note: Does not refresh automatically")
        
        dataplot1x = []
        dataplot1y = []
        dataplot2x = []
        dataplot2y = []
        dataplot3x = []
        dataplot3y = []
        
        dataplot1x, dataplot1y, dataplot2x, dataplot2y, dataplot3x, dataplot3y  = winbudget.getTableData()
     
        
        vr.addValue(f"{wtag}_dataplot1x", dataplot1x)
        vr.addValue(f"{wtag}_dataplot1y", dataplot1y)
        vr.addValue(f"{wtag}_dataplot2x", dataplot2x)
        vr.addValue(f"{wtag}_dataplot2y", dataplot2y)   
        vr.addValue(f"{wtag}_dataplot3x", dataplot3x)
        vr.addValue(f"{wtag}_dataplot3y", dataplot3y)     
        
            
        
        with dpg.group(horizontal=True):
        
            # create plot 1
            with dpg.plot(no_title=True, no_mouse_pos=True, width=0.4 * cfg.w, height=0.4 * cfg.w):
                dpg.bind_colormap(dpg.last_item(), dpg.mvPlotColormap_Default)
                # create legend
                dpg.add_plot_legend()
                # create x axis
                dpg.add_plot_axis(dpg.mvXAxis, label="Expense Budget By Root (Top 10)", no_gridlines=True, no_tick_marks=True, no_tick_labels=True)
                dpg.set_axis_limits(dpg.last_item(), 0, 1)
                # create y axis
                with dpg.plot_axis(dpg.mvYAxis, label="", no_gridlines=True, no_tick_marks=True, no_tick_labels=True):
                    dpg.set_axis_limits(dpg.last_item(), 0, 1)
                    dpg.add_pie_series(0.5, 0.5, 0.5, vr.getValue(f"{wtag}_dataplot1y"), vr.getValue(f"{wtag}_dataplot1x"), normalize=True, tag=f"{wtag}_dataplot1")
                    
            # create plot 2
            with dpg.plot(no_title=True, no_mouse_pos=True, width=0.4 * cfg.w, height=0.4 * cfg.w):
                dpg.bind_colormap(dpg.last_item(), dpg.mvPlotColormap_Default)
                # create legend
                dpg.add_plot_legend()
                # create x axis
                dpg.add_plot_axis(dpg.mvXAxis, label="Expense Budget By Category (Top 10)", no_gridlines=True, no_tick_marks=True, no_tick_labels=True)
                dpg.set_axis_limits(dpg.last_item(), 0, 1)
                # create y axis
                with dpg.plot_axis(dpg.mvYAxis, label="", no_gridlines=True, no_tick_marks=True, no_tick_labels=True):
                    dpg.set_axis_limits(dpg.last_item(), 0, 1)
                    dpg.add_pie_series(0.5, 0.5, 0.5, vr.getValue(f"{wtag}_dataplot2y"), vr.getValue(f"{wtag}_dataplot2x"), normalize=True, tag=f"{wtag}_dataplot2")
        
        dpg.add_separator()
        with dpg.group(horizontal=True):
        
            # create plot 3
            with dpg.plot(no_title=True, no_mouse_pos=True, width=0.4 * cfg.w, height=0.4 * cfg.w):
                dpg.bind_colormap(dpg.last_item(), dpg.mvPlotColormap_Default)
                # create legend
                dpg.add_plot_legend()
                # create x axis
                dpg.add_plot_axis(dpg.mvXAxis, label="Income Budget By Category (Top 10)", no_gridlines=True, no_tick_marks=True, no_tick_labels=True)
                dpg.set_axis_limits(dpg.last_item(), 0, 1)
                # create y axis
                with dpg.plot_axis(dpg.mvYAxis, label="", no_gridlines=True, no_tick_marks=True, no_tick_labels=True):
                    dpg.set_axis_limits(dpg.last_item(), 0, 1)
                    dpg.add_pie_series(0.5, 0.5, 0.5, vr.getValue(f"{wtag}_dataplot3y"), vr.getValue(f"{wtag}_dataplot3x"), normalize=True, tag=f"{wtag}_dataplot3")
                    
            # create plot 4
            with dpg.plot(no_title=True, no_mouse_pos=True, width=0.4 * cfg.w, height=0.4 * cfg.w):
                dpg.bind_colormap(dpg.last_item(), dpg.mvPlotColormap_Default)
                # create legend
                dpg.add_plot_legend()
                # create x axis
                dpg.add_plot_axis(dpg.mvXAxis, label="Expense Error", no_gridlines=True, no_tick_marks=True, no_tick_labels=True)
                dpg.set_axis_limits(dpg.last_item(), 0, 1)
                # create y axis
                with dpg.plot_axis(dpg.mvYAxis, label="", no_gridlines=True, no_tick_marks=True, no_tick_labels=True):
                    dpg.set_axis_limits(dpg.last_item(), 0, 1)
                    dpg.add_pie_series(0.5, 0.5, 0.5, vr.getValue(f"{wtag}_dataplot2y"), vr.getValue(f"{wtag}_dataplot2x"), normalize=True, tag=f"{wtag}_dataplot4")
        dpg.add_separator()
        
        ## Summary
        dpg.add_text(f"Budget Summary")
        btotaltxt = dpg.add_text(f"Total Budget: ${vr.getValue(btotalTag)}")
        binctxt = dpg.add_text(f"Total Budgeted Income: ${vr.getValue(bincTag)}")
        dpg.add_text(f"30 Day Change: ${thirtyDaySum}")
        dpg.add_text(f"90 Day Change: ${nintyDaySum}")
        dpg.add_separator()
        ## Budget Editing Table
        tableTag = f"{wtag}_table"
        dpg.add_text("Budget Editor (Monthly)")
        dpg.add_button(label="Save Budget", callback=saveBudgetToFile, user_data=winuser)
        
        
        dataForHeatmap = []
        
        with dpg.table(header_row=True, row_background=True,
                   borders_innerH=False, borders_outerH=False, borders_innerV=True,
                   borders_outerV=True, sortable=False, tag=tableTag):
            dpg.add_table_column(label="Root Category", width_stretch=True, init_width_or_weight=1.0)
            dpg.add_table_column(label="Category", width_stretch=True, init_width_or_weight=1.0)
            dpg.add_table_column(label="Budget", width_stretch=True, init_width_or_weight=0.2)
            dpg.add_table_column(label="30 day", width_stretch=True, init_width_or_weight=0.3)
            dpg.add_table_column(label="90 day", width_stretch=True, init_width_or_weight=0.3)
            dpg.add_table_column(label="90 day Difference", width_stretch=True, init_width_or_weight=0.3)
            dpg.add_table_column(label="Edit", width_stretch=True, init_width_or_weight=0.3)
            
            #ttype = cfc.tranactionClasses()
            budgetCatList = winuser.budget.getListOfCategoriesKeysWithType()
            
            
            
            row = 0
            for budgetCat in budgetCatList:
                t = None
                with dpg.table_row():
                    cat = budgetCat[1].split("-")[1]
                    root = budgetCat[1].split("-")[0]
                    typeofcat = budgetCat[0]
                    
                    dpg.add_text(f"{root}")
                    if typeofcat == "income":
                        dpg.highlight_table_cell(tableTag, row, 0, [0, 50, 0, 100])
                    else:
                        dpg.highlight_table_cell(tableTag, row, 0, [50, 0, 0, 100])
                        
                    dpg.add_text(f"{cat}")
                    if typeofcat == "income":
                        dpg.highlight_table_cell(tableTag, row, 1, [0, 50, 0, 100])
                    else:
                        dpg.highlight_table_cell(tableTag, row, 1, [50, 0, 0, 100])
                    t = dpg.add_text(f"{winbudget.getBudgetForCategory(cat, root)}")
                    
                    #30 day
                    val30 = f"---"
                    key = f"{root}-{cat}"
                    if key in thirtyDay:
                        val30 = thirtyDay[key]
                        #round to 2 decimal places
                        val30 = str(round(float(val30), 2))
                    dpg.add_text(val30)
                    
                    val90 = f"---"
                    key = f"{root}-{cat}"
                    if key in nintyDay:
                        val90 = nintyDay[key]
                        #round to 2 decimal places
                        val90 = str(round(float(val90), 2))
                    dpg.add_text(val90)
                    
                    #between budget and 90 day / 3 day
                    diffbetween = f"---"
                    actual90 = 0
                    budgetted30 = winbudget.values[key]
                    
                    if val90 != f"---":
                        actual90 = float(val90)
                    
                    if budgetted30 != 0 or actual90 != 0:
                        actual30 = round((actual90/3),2)
                        
                        
                        if typeofcat == 'expense':
                            diffbetween = round(abs(budgetted30) - abs(actual30) ,2)
                            if actual30 > budgetted30:
                                diffbetween = diffbetween * -1
                        else:
                            diffbetween = round(abs(actual30) - abs(budgetted30) ,2)
                            if actual30 < budgetted30:
                                diffbetween = diffbetween * -1
                        dataForHeatmap.append((diffbetween, budgetted30))
                        #print(f"Root: {root} | Cat: {cat} | Actual: {actual90} | Budget: {budgetted30}| Diff: {diffbetween}|type: {typeofcat}")       
                        dpg.add_text(diffbetween)
                        dpg_highlight_table_cell(tableTag, diffbetween, row, 5, mul=3)
                    
                        #print(f"Name: {cat} | Budget: {budgetted30} | Actual: {actual30} | Diff: {diffbetween} | isIncome: {isIncome}")
                    else:
                        dpg.add_text("")
                    
                    
                    with dpg.table_cell():
                        with dpg.group(horizontal=True):
                            defaultVal = winbudget.getBudgetForCategory(cat, root)
                            b = dpg.add_button(label="Edit")
                            #dpg.set_item_user_data(b, t)
                            with dpg.popup(b, tag=f"{wtag}_btable1_popup_{row}", mousebutton=dpg.mvMouseButton_Left, modal=True):
                                dpg.add_text("Adjust Budget")
                                dpg.add_separator()
                                
                                txtf = dpg.add_input_int(label="Budget", default_value=defaultVal,
                                                  callback=cb_setBudgetTableValue, user_data=(t, cat, root, winbudget, btotalTag, bincTag, btotaltxt, binctxt, wtag, winuser))
                                with dpg.group(horizontal=True):
                                    dpg.add_button(label="Reset to 0", callback=cb_budget_resetCat, user_data=(t, cat, root, winbudget, btotalTag, bincTag, btotaltxt, binctxt, wtag, winuser, f"{wtag}_btable1_popup_{row}", txtf))
                                    dpg.add_button(label="Close", callback=cb_CloseWindow, user_data=f"{wtag}_btable1_popup_{row}")
                row += 1
        dpg.add_separator()
        
        valuesheatmap = []
        #sort dataforheatmap by value (first item in tuple)
        dataForHeatmap.sort(key=lambda tup: tup[0])
        for i in range(len(dataForHeatmap)):
            val = dataForHeatmap[i][0]
            budget = dataForHeatmap[i][1]
            #normalize between 0 to 0.5 if in budget, 1 if no spending, 0 to -0.5 if over budget, -1 if no budget
            valueCell = 0
            if budget != 0:
                
                if budget >= val:
                    valueCell = 1 - (val/budget)
                    #clamp between 0 and 0.5
                    valueCell = max(valueCell, 0.5)
                elif budget < val:
                    valueCell = 1 - (val/budget)
                    #clamp between -0.5 to 0
                    valueCell = min(valueCell, -0.5)
                valuesheatmap.append(valueCell)
            else:
                if val > 0:
                    valueCell = 1
                    valuesheatmap.append(valueCell)
                else:
                    valueCell = -1
                    valuesheatmap.append(valueCell)
        lendata = len(valuesheatmap)
        squaredim = ceil(sqrt(lendata))
        missingcells = (squaredim * squaredim) - lendata
        for i in range(missingcells):
            valuesheatmap.append(0)
        
        dpg.add_text("0 to 0.5 for budgeted, 1 for no spending, 0 to -0.5 for over budget, -1 for no budget")
        with dpg.group(horizontal=True):
            
            
            dpg.add_colormap_scale(min_scale=-1, max_scale=1, height=400)
            dpg.bind_colormap(dpg.last_item(), 'redgreen')
            with dpg.plot(label="Budget Heatmap", no_mouse_pos=True, height=400, width=-1):
                dpg.bind_colormap(dpg.last_item(), 'redgreen')
                dpg.add_plot_axis(dpg.mvXAxis, label="x", lock_min=True, lock_max=True, no_gridlines=True, no_tick_marks=True)
                with dpg.plot_axis(dpg.mvYAxis, label="y", no_gridlines=True, no_tick_marks=True, lock_min=True, lock_max=True):
                    dpg.add_heat_series(valuesheatmap, squaredim, squaredim, scale_min=-1, scale_max=1)
                    
        
        #set window to be large enough to fit the table
        dpg.set_item_width(wtag, 0.9 * cfg.w)
        dpg.set_item_height(wtag, 0.9 * cfg.h)
        dpg.set_item_pos(wtag, (0.05 * cfg.w, 0.05 * cfg.h))
                
     
def cb_budget_resetCat(sender, app_data, user_data):
    text = user_data[0]
    root = user_data[2]
    cat = user_data[1]
    budget : cfc.BudgetSet = user_data[3]
    btotalTag = user_data[4]
    bincTag = user_data[5]
    btotaltxt = user_data[6]
    binctxt = user_data[7]
    wtag = user_data[8]
    winuser = user_data[9]
    closeWindowTag = user_data[10]
    wtag_data1 = f"{wtag}_dataplot1"
    wtag_data2 = f"{wtag}_dataplot2"
    value = 0
    #recalc values
    budget.setBudgetForCategory(cat, root, value)
    btotal = budget.getAllSummed()
    binc = budget.getAllOfKey("Income")
    #change label
    dpg.set_value(text, value)  
    txtf = user_data[11]
    dpg.set_value(txtf, value)  
    #change value in budget
    
    vr.addValue(btotalTag, btotal)
    vr.addValue(bincTag, binc)
    btotaltxt = dpg.set_value(btotaltxt, f"Total Budget: ${btotal}")
    binctxt = dpg.set_value(binctxt, f"Total Budgeted Income: ${binc}")
    
    #update pies
    dataplot1x, dataplot1y, dataplot2x, dataplot2y, dataplot3x, dataplot3y  = budget.getTableData()
    
    
     
        
    vr.addValue(f"{wtag}_dataplot1x", dataplot1x)
    vr.addValue(f"{wtag}_dataplot1y", dataplot1y)
    vr.addValue(f"{wtag}_dataplot2x", dataplot2x)
    vr.addValue(f"{wtag}_dataplot2y", dataplot2y)   
    vr.addValue(f"{wtag}_dataplot3x", dataplot3x)
    vr.addValue(f"{wtag}_dataplot3y", dataplot3y)       
    #save data to file
    saveBudgetToFile(sender, app_data, winuser)
    
    #close window
    cb_CloseWindow(sender, app_data, closeWindowTag)
    
    
def cb_setBudgetTableValue(sender, app_data, user_data):
    text = user_data[0]
    root = user_data[2]
    cat = user_data[1]
    budget : cfc.BudgetSet = user_data[3]
    btotalTag = user_data[4]
    bincTag = user_data[5]
    btotaltxt = user_data[6]
    binctxt = user_data[7]
    wtag = user_data[8]
    winuser = user_data[9]
    wtag_data1 = f"{wtag}_dataplot1"
    wtag_data2 = f"{wtag}_dataplot2"
    value = dpg.get_value(sender)
    #recalc values
    budget.setBudgetForCategory(cat, root, value)
    btotal = budget.getAllSummedNonIncome()
    binc = budget.getAllSummedIncome()
    #change label
    dpg.set_value(text, value)    
    #change value in budget
    
    vr.addValue(btotalTag, btotal)
    vr.addValue(bincTag, binc)
    btotaltxt = dpg.set_value(btotaltxt, f"Total Budget: ${btotal}")
    binctxt = dpg.set_value(binctxt, f"Total Budgeted Income: ${binc}")
    
    #update pies
    dataplot1x, dataplot1y, dataplot2x, dataplot2y, dataplot3x, dataplot3y  = budget.getTableData()
    
    
     
        
    vr.addValue(f"{wtag}_dataplot1x", dataplot1x)
    vr.addValue(f"{wtag}_dataplot1y", dataplot1y)
    vr.addValue(f"{wtag}_dataplot2x", dataplot2x)
    vr.addValue(f"{wtag}_dataplot2y", dataplot2y)   
    vr.addValue(f"{wtag}_dataplot3x", dataplot3x)
    vr.addValue(f"{wtag}_dataplot3y", dataplot3y)       
    #save data to file
    saveBudgetToFile(sender, app_data, winuser)
    
    
    
    
    
#saves budget to user folder
def saveBudgetToFile(sender, app_data, user_data):
    user = user_data
    if user == None:
        user = dh.currentuser
    print(f"[Coinflow] Saving budget for {user.name}")
    budget = user.budget
    #write to json file
    if not os.path.exists(user.path):
        os.makedirs(user.path)
    userBudgetPath = os.path.join(user.path, 'budget.json')
    with open(userBudgetPath, "w") as f:
        json.dump(budget.values, f)  
        f.close()   

#endregion


#region Rules window callbacks
def cb_CreateRulesWindow(sender, app_data, user_data):
    wh.addWindow("RulesCats", (100, 100))
    #wh.listWindows()
    wtag = wh.getTagForId(wh.winidx)
    #get context
    winuser = dh.currentuser
    with dpg.window(label="RulesCats", tag=wtag, width=500, height=500):
        dpg.add_text("Rules")
        dpg.add_text(f"Changes in {cfg.rulesFileName} will be applied on next login.")
        
        dpg.add_separator()
        tableTag = f"{wtag}_table"

        with dpg.table(tag=tableTag, header_row=True, borders_innerH=True, borders_outerH=True,
                       borders_innerV=True, borders_outerV=True, resizable=True, reorderable=True):
            dpg.add_table_column(label="Match", width_stretch=True, init_width_or_weight=2)
            dpg.add_table_column(label="Category", width_stretch=True, init_width_or_weight=2)
            dpg.add_table_column(label="Filter By", width_stretch=True, init_width_or_weight=1)
            dpg.add_table_column(label="Filter Income", width_stretch=True, init_width_or_weight=1)
            dpg.add_table_column(label="Filter Type", width_stretch=True, init_width_or_weight=1)
            
            
            #add rows
            for rule in dh.users.rules.rules:
                with dpg.table_row():
                    dpg.add_text(rule.rulestr)
                    dpg.add_text(rule.ruleMatchValue)
                    dpg.add_text(rule.ruleMatchType)
                    dpg.add_text(rule.rulematchwithtype)
                    dpg.add_text(rule.ruleType)
                    
        dpg.add_separator()
        dpg.add_text(f"List of Categories (Change in {cfg.categoriesFileName} will be applied on next login.)")
        
        allcats = dh.currentuser.budget.getListOfCategoriesKeysWithType()
        allincomeRoots = list()
        allExpenseRoots = list()
        allNeutralRoots = list()
        for cat in allcats:
            typeOfCat = cat[0]
            root = cat[1].split("-")[0]
            category = cat[1].split("-")[1]
            if root not in allincomeRoots and typeOfCat == "income":
                allincomeRoots.append(root)
            elif root not in allExpenseRoots and typeOfCat == "expense":
                allExpenseRoots.append(root)
            elif root not in allNeutralRoots and typeOfCat == "neutral":
                allNeutralRoots.append(root)
        #make treenode
        with dpg.tree_node(label="Categories"):
            with dpg.tree_node(label='income', tag=f"{wtag}_income"):
                for root in allincomeRoots:
                    with dpg.tree_node(label=f"{root}", tag=f"{wtag}_income_{root}"):
                        pass
                        
            with dpg.tree_node(label='expense', tag=f"{wtag}_expense"):
                for root in allExpenseRoots:
                    with dpg.tree_node(label=f"{root}", tag=f"{wtag}_expense_{root}"):
                        pass
            with dpg.tree_node(label='neutral', tag=f"{wtag}_neutral"):
                for root in allNeutralRoots:
                    with dpg.tree_node(label=f"{root}", tag=f"{wtag}_neutral_{root}"):
                        pass
                    
            for cat in allcats:
                typeOfCat = cat[0]
                root = cat[1].split("-")[0]
                category = cat[1].split("-")[1]

                if typeOfCat == "income":
                    dpg.add_text(f"{root} - {category}", parent=f"{wtag}_income_{root}")
                elif typeOfCat == "expense":
                    dpg.add_text(f"{root} - {category}", parent=f"{wtag}_expense_{root}")
                elif typeOfCat == "neutral":
                    dpg.add_text(f"{root} - {category}", parent=f"{wtag}_neutral_{root}")
                    
        
        #print(budget)
    #set window to be large enough to fit the table
        dpg.set_item_width(wtag, 0.7 * cfg.w)
        dpg.set_item_height(wtag, 0.75 * cfg.h)
        dpg.set_item_pos(wtag, (0.05 * cfg.w, 0.05 * cfg.h))
                    
        
        
        
        
    
#endregion


#region Config  Window Callbacks

def cb_txtinputUser(sender, app_data, user_data):
    #get text
    txtval = dpg.get_value(sender).strip()
    #set text from userdata
    dpg.set_value(user_data, "Selected User: " + txtval)
    #sets in config file
    cfg.currentDefaultUser = txtval
    with open(cfg.configPath, "w") as f:
        json.dump(cfg.__dict__, f)  
        f.close()
        
def cb_txtinputAcc(sender, app_data, user_data):
    #get text
    txtval = dpg.get_value(sender).strip()
    #set text from userdata
    dpg.set_value(user_data, "Selected Account: " + txtval)
    #sets in config file
    cfg.currentDefaultAccount = txtval
    with open(cfg.configPath, "w") as f:
        json.dump(cfg.__dict__, f)  
        f.close()
    
    
def cb_regenUsrCfg(sender, app_data, user_data):
    username = user_data[0].name
    accname = user_data[1].nameOfAccount
    newcfg = cfs.usrconfigjson("Default User Name")
    dh.createNewUserConfig(username, newcfg)
    print(f"[Coinflow] Regenerated User Configs for {username}")
    
def cb_regenAcCfg(sender, app_data, user_data):
    username = user_data[0].name
    accname = user_data[1].nameOfAccount
    
    newcfg = cfs.acconfigjson("Default Account Name", actype=str(cfparse.AccountType.Credit))
    dh.createNewAccountConfig(username, accname, newcfg)
    print(f"[Coinflow] Regenerated Account Configs for {username} / {accname}")
    
def cb_regenProgCfg(sender, app_data, user_data):
    cfg = cfs.pgrmconfigjson()
    dh.createNewProgramConfig(cfg)
    print(f"[Coinflow] Regenerating Program Configs")

def cb_optionsSetL2(sender, app_data, user_data):
    value = dpg.get_value(sender)
    value = abs(round(float(value),2))
    cfg.l2transactionAmount = value
    programcfg = cfs.pgrmconfigjson()
    programcfg.l2transactionAmount = value
    pcfg = ConfigToProgramCfg(cfg)
    dh.createNewProgramConfig(pcfg)
    print(f"[Coinflow] Set Medium Transaction Amount to {value}")
    
def cb_optionsSetL3(sender, app_data, user_data):
    value = dpg.get_value(sender)
    value = abs(round(float(value),2))
    cfg.l3transactionAmount = value
    pcfg = ConfigToProgramCfg(cfg)
    dh.createNewProgramConfig(pcfg)
    print(f"[Coinflow] Set Large Transaction Amount to {value}")
    
def ConfigToProgramCfg(config: ConfigSettings):
    #converts config to program config
    pcfg = cfs.pgrmconfigjson()
    pcfg.defaultAccount = config.currentDefaultAccount
    pcfg.defaultUser = config.currentDefaultUser
    pcfg.defaultL2TransactionAmount = config.l2transactionAmount
    pcfg.defaultL3TransactionAmount = config.l3transactionAmount
    pcfg.defaultWindow_w = config.w
    pcfg.defaultWindow_h = config.h
    pcfg.defaultIsFullScreen = config.isFullScreen
    pcfg.defaultDataFolderName = config.dataFolderName
    pcfg.defaultconfigFileName = config.configFileName
    pcfg.defaultbackupFolderName = config.backupFolderName
    pcfg.defaultrulesFileName = config.rulesFileName
    pcfg.defaultcategoriesFileName = config.categoriesFileName
    pcfg.defaultstocksFileName = config.stocksFileName
    return pcfg


def cb_regenUsrBud(sender, app_data, user_data):
    user = user_data[0]
    
    budgetPath = os.path.join(user.path, 'budget.json')
    newbudget = cfc.BudgetSet()
    with open(budgetPath, 'w') as json_file:
        json.dump(newbudget.values, json_file)
        print(f"[Coinflow] Regenerating budget file for user: {user.name}")
        json_file.close()    
    user.budget = newbudget 

def cb_CreateConfigWindow(sender, app_data, user_data):
    #set windows
    wh.addWindow("Options Configs", (100, 100))
    #wh.listWindows()
    wtag = wh.getTagForId(wh.winidx)
    #get context
    winuser = dh.currentuser
    winacc = dh.currentuser.currentAccount
    winbudget = winuser.budget
    
    with dpg.window(label="Budget", pos=(100, 100), tag=wtag, width=600, height=500):
        dpg.add_text("Options Configs")
        
        with dpg.tree_node(label="Program Configs", selectable=True):
            defaultuser = cfg.currentDefaultUser
            defaultacc = cfg.currentDefaultAccount
            dpg.add_text(f"Selected User: {winuser.name}", tag=f"{wtag}_defaultusertxt")
            dpg.add_text(f"Selected Account: {winacc.nameOfAccount}", tag=f"{wtag}_defaultaccttxt")
            dusertxt = dpg.add_input_text(label="Default User", default_value=defaultuser, callback=cb_txtinputUser, user_data=f"{wtag}_defaultusertxt", no_spaces=True)
            dacctxt = dpg.add_input_text(label="Default Account", default_value=defaultacc, callback=cb_txtinputAcc, user_data=f"{wtag}_defaultaccttxt", no_spaces=True)
            with dpg.item_handler_registry() as registry:
                dpg.add_item_clicked_handler(button=dpg.mvMouseButton_Right, callback=right_click_context_menu, user_data=dusertxt)
                dpg.bind_item_handler_registry(dusertxt, registry)
                dpg.add_item_clicked_handler(button=dpg.mvMouseButton_Right, callback=right_click_context_menu, user_data=dacctxt)
                dpg.bind_item_handler_registry(dacctxt, registry)
            
            dpg.add_text("Used for highlighting transactions")
            dpg.add_input_float(label="Medium Transaction Amount", default_value=cfg.l2transactionAmount, callback=cb_optionsSetL2, min_clamped=True, min_value=0)
            dpg.add_input_float(label="Large Transaction Amount", default_value=cfg.l3transactionAmount, callback=cb_optionsSetL3, min_clamped=True, min_value=0)
        with dpg.tree_node(label="Reset Configs to Default", selectable=True):
            dpg.add_text(f"Selected User: {winuser.name}", tag=f"{wtag}_resetusertxt")
            dpg.add_text(f"Selected Account: {winacc.nameOfAccount}", tag=f"{wtag}_resetaccttxt")
            
            dpg.add_button(label="Reset Program Configs", callback=cb_regenProgCfg)
            dpg.add_button(label="Reset User Configs", callback=cb_regenUsrCfg, user_data=(winuser, winacc))
            dpg.add_button(label="Reset User Budget", callback=cb_regenUsrBud, user_data=(winuser))
            dpg.add_button(label="Reset Account Configs", callback=cb_regenAcCfg, user_data=(winuser, winacc))
        
        
     #set window to be large enough to fit the table
    dpg.set_item_width(wtag, 0.5 * cfg.w)
    dpg.set_item_height(wtag, 0.5 * cfg.h)
    dpg.set_item_pos(wtag, (0.05 * cfg.w, 0.05 * cfg.h))
    
    
#endregion

#region Import CSV Window
def cb_CreateImportWindow(sender, app_data, user_data):
    #get window
    wh.addWindow("Import CSV", (100, 100))
    #wh.listWindows()
    wtag = wh.getTagForId(wh.winidx)
    #get context
    winuser = dh.currentuser
    winacc = dh.currentuser.currentAccount
    with dpg.window(label="Import CSV", pos=(100, 100), tag=wtag, width=600, height=500):
        dpg.add_text("Import CSV")
        dpg.add_text("Select a CSV file to import")
        
        #with dpg.add_file_dialog(label="Select CSV File", show=True, callback=lambda s, a, u : print(s, a, u), tag=wtag + "filedialog"):
        #    dpg.add_file_extension(".*", color=(255, 255, 255, 255))
        #    dpg.add_file_extension("Comma Seperated (*.csv){.csv,.CSV}", color=(0, 255, 255, 255))
        #dpg.add_button(label="Show File Selector", user_data=dpg.last_container(), callback=lambda s, a, u: dpg.configure_item(u, show=True))
        
        with dpg.file_dialog(label="Select CSV File", width=700, height=500, show=False, callback=cb_handleImportCSV, tag=f"{wtag}_filedialog", user_data=(winuser, winacc, wtag)):
            
            #dpg.add_file_extension("Source files (*.cpp *.h *.hpp){.cpp,.h,.hpp}", color=(0, 255, 255, 255))
            dpg.add_file_extension("Comma Seperated (*.csv){.csv,.CSV}", color=(0, 255, 255, 255))
            dpg.add_file_extension(".*", color=(255, 255, 255, 255))
            #dpg.add_file_extension(".h", color=(255, 0, 255, 255), custom_text="header")
            #dpg.add_file_extension("Python(.py){.py}", color=(0, 255, 0, 255))
            #dpg.add_button(label="Button on file dialog")

        dpg.add_button(label="Show File Selector", user_data=dpg.last_container(), callback=lambda s, a, u: dpg.configure_item(u, show=True))
        #with dpg.file_dialog(label="Demo File Dialog", width=300, height=400, show=False, callback=lambda s, a, u : print(s, a, u), tag="__demo_filedialog"):
        #            dpg.add_file_extension(".*", color=(255, 255, 255, 255))
        #            dpg.add_file_extension("Source files (*.cpp *.h *.hpp){.cpp,.h,.hpp}", color=(0, 255, 255, 255))
        #            dpg.add_file_extension(".cpp", color=(255, 255, 0, 255))
        #            dpg.add_file_extension(".h", color=(255, 0, 255, 255), custom_text="header")
        #            dpg.add_file_extension("Python(.py){.py}", color=(0, 255, 0, 255))
        #            #dpg.add_button(label="Button on file dialog")

              
        
     #set window to be large enough to fit the table

def cb_handleImportCSV(sender, app_data, user_data):
    filepathname = app_data['file_path_name']
    filename = app_data['file_name']
    currentpath = app_data['current_path']
    currentfilter = app_data['current_filter']
    minsize = app_data['min_size']
    maxsize = app_data['max_size']
    selections = app_data['selections']
    user = user_data[0]
    acc = user_data[1]
    wtag = user_data[2]
    destpath = os.path.join(os.getcwd(), cfg.dataFolderName, user.name, acc.nameOfAccount)
    status = ''
    #check if already exists
    if os.path.exists(os.path.join(destpath, filename)):
        print(f"[Coinflow] File already exists in destination folder: {destpath}")
        status = f"File already exists in destination folder:\n{destpath}"
    else:
        #copy file to destination folder
        os.makedirs(destpath, exist_ok=True)
        os.system(f"copy \"{filepathname}\" \"{destpath}\"")
        print(f"[Coinflow] File copied to destination folder: {destpath}")
        status = f"File copied to destination folder:\n{destpath},\n Please Relaunch Coinflow to see changes"
        
    #display status
    with dpg.window(label="Import Status", pos=(cfg.w * 0.2, cfg.h * 0.2), tag=f"{wtag}_importcsv", width=500, height=200):
        dpg.add_text("Import Status")
        dpg.add_text(status)
        dpg.add_button(label="Close", callback=cb_CloseWindow, user_data=f"{wtag}_importcsv")
    
    

#endregion


#region General Functions and callbacks

def sanitizeString(string=""):
    #only allow letters, numbers, and underscores
    if string == "":
        return string
    
    for char in string:
        if char != "_" and not char.isalnum():
            string = string.replace(char, "")
            
    
    return string.strip().lower()
                
def cb_CloseWindow(sender, app_data, user_data):
    #given a window tag, close the window
    print(f"[Coinflow] Closing window: {user_data}")
    dpg.configure_item(user_data, show=False)
    
def cb_CloseMultipleWindows(sender, app_data, user_data):
    for wtag in user_data:
        dpg.configure_item(wtag, show=False)

def cb_DeleteWindow(sender, app_data, user_data):
    #given a window tag, delete the window
    print(f"[Coinflow] Deleting window: {user_data}")
    dpg.delete_item(user_data)

def cb_ChangeFont(sender, app_data, user_data):
    if user_data == "Moon Light":
        dpg.bind_font(default_font)
    elif user_data == "Roboto":
        dpg.bind_font(sec_font)
            
def cb_BackupData(sender, app_data, user_data):
    print(f"[Coinflow] Backing up data")
    status = 'Unknown Error :O'
    todaydate = datetime.datetime.now().strftime("%Y_%m_%d")
    print(f"[Coinflow] Today's date: {todaydate}")
    backupFolder = cfg.backupFolderName
    backupPath = os.path.join(os.getcwd(), backupFolder, todaydate)
    #check if folder exists
    maxIterations = 20
    bkidx = 1
    citerations = 1
    while os.path.exists(backupPath) and citerations < maxIterations:
        print(f"Checking if backup folder exists: {backupPath}")
        backupPath = os.path.join(os.getcwd(), backupFolder, todaydate + f"_{bkidx}")
        citerations += 1
        bkidx += 1
        
    cfs.Logger().log(f"Backup Path: {backupPath}", "INFO")
    
    #make ./backup folder if it doesn't exist
    if not os.path.exists(os.path.join(os.getcwd(), backupFolder)):
        os.makedirs(os.path.join(os.getcwd(), backupFolder))
    
    #make backup folder
    try:
        if not os.path.exists(backupPath):
            os.makedirs(backupPath)
            #copy in data folder, rules, categories, config
            #copy data folder
            shutil.copytree(os.path.join(os.getcwd(), cfg.dataFolderName), os.path.join(backupPath, cfg.dataFolderName))
            #copy rules
            shutil.copy(os.path.join(os.getcwd(), cfg.rulesFileName), os.path.join(backupPath, cfg.rulesFileName))
            #copy categories
            shutil.copy(os.path.join(os.getcwd(), cfg.categoriesFileName), os.path.join(backupPath, cfg.categoriesFileName))
            #copy config
            shutil.copy(os.path.join(os.getcwd(), cfg.configFileName), os.path.join(backupPath, cfg.configFileName))
            #copy stocks
            shutil.copy(os.path.join(os.getcwd(), cfg.stocksFileName), os.path.join(backupPath, cfg.stocksFileName))
            status = f"Backup Successful:\n{backupPath}"
            
    except Exception as e:
        status = f"Backup Failed:\n{e}"
        
    #display status
    wh.addWindow("Transactions", (100, 100))
    wtag = wh.getTagForId(wh.winidx)   
    with dpg.window(label="Backup Status", pos=(cfg.w * 0.2, cfg.h * 0.2), tag=wtag, width=500, height=200):
        dpg.add_text("Backup Status")
        dpg.add_text(status)
        dpg.add_button(label="Close", callback=cb_CloseWindow, user_data=wtag)
    
    




def wrapper_addUser(name=""):
    #add menu item to menu using tag
    usersmenuTag = 'g_menu_users'
    #get menu from tag
    dpg.add_menu_item(parent=g_menu_users, label=name, callback=cb_ChangeUser, user_data=name)
    userid = dh.users.addUser(name)
    #add account to user
    dh.currentuser = dh.users.getUserByName(name)
    Checking = cfparse.Account('a_checking', 0, 0, cfparse.AccountType.Checking)
    dh.users.addUserAccount(userid, Checking)
    dh.currentuser.currentAccount = Checking
    
    #create new folder for user
    dh.createNewUserFolders(name)
    dh.createNewAccountFolders(name, 'a_checking')
    
    #create configs
    usrConfig = cfs.usrconfigjson(name)
    dh.createNewUserConfig(name, usrConfig)
    acConfig = cfs.acconfigjson(name, str(Checking.typeOfAccount))
    dh.createNewAccountConfig(name, 'a_checking', acConfig)
    
    regenerateMenuUsers()
    regenerateMenuAccounts()
    
    return userid

def right_click_context_menu(sender, app_data, user_data):
    def copy():
        clipboard.copy(dpg.get_value(user_data))
        dpg.delete_item(popup)

    def paste():
        dpg.set_value(user_data, clipboard.paste())
        dpg.delete_item(popup)

    with dpg.window(popup=True) as popup:
        dpg.add_button(label="Copy", callback=copy)
        dpg.add_button(label="Paste", callback=paste)
#endregion
    
    
#region Stocks Window Callbacks

def cb_CreateStocksWindow(sender, app_data, user_data):
    #set windows
    wh.addWindow("Stocks", (100, 100))
    #wh.listWindows()
    wtag = wh.getTagForId(wh.winidx)
    #get context
    winuser = dh.currentuser
    winacc = dh.currentuser.currentAccount
    winbudget = winuser.budget
    
    with dpg.window(label="Stocks", pos=(100, 100), tag=wtag, width=600, height=500):
        dpg.add_text(f"Stocks are on a per-program basis, defined in {cfg.stocksFileName}\nThey are not saved to the database.")
        #TODO add options for this on time, maybe save stock data in a file for quick load?
        dpg.add_text(f"Stocks require a call to the yahoo yfinance API to get the current price.\nTakes ~4s per 3mo of data (1 stock).")
        dpg.add_button(label="Load Stocks", callback=cb_LoadStocks, user_data=(wtag, f"{wtag}_loadstocks", f"{wtag}_loading", f"{wtag}_group1"), tag=f"{wtag}_loadstocks", show=True)
        dpg.add_loading_indicator(tag=f"{wtag}_loading", show=False)
        
        dpg.add_separator()
        dpg.add_text(f"Stocks Graphs")
        with dpg.group(horizontal=False, tag=f"{wtag}_group1"):
            pass
        
        
        
        
     #set window to be large enough to fit the table
    dpg.set_item_width(wtag, 0.9 * cfg.w)
    dpg.set_item_height(wtag, 0.9 * cfg.h)
    dpg.set_item_pos(wtag, (0.05 * cfg.w, 0.05 * cfg.h))
 
def cb_LoadStocks(sender, app_data, user_data):
    
    wtag = user_data[0]
    loadbuttontag = user_data[1]
    loadindicator = user_data[2]
    grouptag = user_data[3]
    
    #load data
    dpg.configure_item(loadindicator, show=True)
    dpg.configure_item(loadbuttontag, show=False)
    tickersdict, tickerslist = cfstocks.getData()
    dpg.configure_item(loadindicator, show=False)
    numRows = ceil(len(tickerslist) / 2)
    with dpg.subplots(numRows, 2, label="Stock Subplots", parent=grouptag, height=-1, width=-1) as subplots:
        for t in tickerslist:
            data = tickersdict[t]
            t_str = t.upper()
            if t_str == "^GSPC":
                t_str = "S&P 500"
            elif t_str == "^DJI":
                t_str = "Dow Jones"
            elif t_str == "^IXIC":
                t_str = "Nasdaq"
            timedata = data[0]
            closedata = data[1]
            opendata = data[2]
            highdata = data[3]
            lowdata = data[4]
            with dpg.plot(label=f"{t_str} - 3mo", height=600):
                dpg.bind_colormap(dpg.last_item(), dpg.mvPlotColormap_Default)
                dpg.add_plot_legend()
                xaxis = dpg.add_plot_axis(dpg.mvXAxis, label="", time=True)
                with dpg.plot_axis(dpg.mvYAxis, label="USD"):
                    dpg.add_candle_series(timedata, opendata, closedata, lowdata, highdata, label=t_str, time_unit=dpg.mvTimeUnit_Day)
                    dpg.fit_axis_data(dpg.top_container_stack())
                dpg.fit_axis_data(xaxis)
    
    
    
 
#endregion  
    
def main():
    global cfg
    cfg = ConfigSettings()
    global dh
    dh = DataHandler()
    global wh
    wh = WindowHandler()
    global vr
    vr = ValueRegistry()
    
    

    #create the context
    dpg.create_context()
    
    with dpg.colormap_registry(label="Colormap Registry", show=False):
        redgreen = [[255, 0, 0, 255], [0, 255, 0, 255]]
        dpg.add_colormap(redgreen, False, tag="redgreen", label="Red Green Colormap")
        #dpg.add_colormap([[0, 0, 0, 255], [255, 255, 255, 255]], False, tag="colormap_ss2", label="col 2")
    
    #load font
    with dpg.font_registry():
    # first argument ids the path to the .ttf or .otf file
        global default_font
        default_font = dpg.add_font("fonts\Roboto-Regular.ttf", 16)
        #bind dpg font
        global sec_font
        sec_font = dpg.add_font("fonts\Moon Light.otf", 14)
        
        #bind default font
        dpg.bind_font(default_font)
        
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 6, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6, category=dpg.mvThemeCat_Core)
        dpg.bind_theme(global_theme)
    
    #create viewport menubar
    with dpg.viewport_menu_bar():
        with dpg.menu(label="Program"):
            dpg.add_menu_item(label="Import CSV", callback=cb_CreateImportWindow)
            dpg.add_menu_item(label="Backup", callback=cb_BackupData)

            with dpg.menu(label="User"):
                #add user
                dpg.add_menu_item(label="Add User", callback=cb_CreateUserWindow)
                dpg.add_menu_item(label="Remove User", callback=cb_deleteUserWindow)
                with dpg.menu(label="Users", tag="menu_users"): 
                    global g_menu_users
                    with dpg.group() as g_menu_users:
                        pass
                    regenerateMenuUsers()
                        
            with dpg.menu(label="Account"):
                dpg.add_menu_item(label="Add Account", callback=cb_CreateAccountWindow)
                dpg.add_menu_item(label="Remove Account", callback=cb_deleteAccWindow)
                with dpg.menu(label="Account", tag="menu_accounts"):
                    global g_menu_accounts
                    with dpg.group() as g_menu_accounts:
                        pass
                    regenerateMenuAccounts()
        
        
        #with dpg.menu(label="File"):
        #    dpg.add_menu_item(label="Save", callback=saveBudgetToFile)
        #    dpg.add_menu_item(label="Import", callback=button_callback)
            
                    
                
        with dpg.menu(label="Create"):
            dpg.add_menu_item(label="Tranactions", callback=cb_CreateTranactionsWindow)
            dpg.add_menu_item(label="Balance", callback=cb_CreateRunningBalanceWindow)
            dpg.add_menu_item(label="Budget", callback=cb_CreateBudgetWindow)
            dpg.add_menu_item(label="Rules", callback=cb_CreateRulesWindow)
            dpg.add_menu_item(label="Stocks", callback=cb_CreateStocksWindow)
            
        with dpg.menu(label="Debug"):
            dpg.add_menu_item(label="Show Debug", callback=cb_callDebugWindow, user_data="debug")
            dpg.add_menu_item(label="Show Metrics", callback=cb_callDebugWindow, user_data="show_metrics")
            dpg.add_menu_item(label="Show About", callback=cb_callDebugWindow, user_data="show_about")
            dpg.add_menu_item(label="Show Documentation", callback=cb_callDebugWindow, user_data="show_documentation")
            dpg.add_menu_item(label="Show Style Editor", callback=cb_callDebugWindow, user_data="show_style_editor")
            dpg.add_menu_item(label="Show Font Manager", callback=cb_callDebugWindow, user_data="show_font_manager")
            dpg.add_menu_item(label="Show Item Registry", callback=cb_callDebugWindow, user_data="item_registry")
            
        with dpg.menu(label="Options"):
            dpg.add_menu_item(label="Fullscreen", callback=cb_ChangeFullscreen, check=True)
            dpg.add_menu_item(label="Open Options Menu", callback=cb_CreateConfigWindow)



    dpg.create_viewport(title=cfg.AppName, width=cfg.w, height=cfg.h, large_icon="assets/copper_coin.ico", small_icon="assets/copper_coin.ico")
    #move viewport to the center of the screen
    dpg.set_viewport_pos((0, 0))
    dpg.setup_dearpygui()
    dpg.show_viewport(maximized=True)
    #dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
    pass