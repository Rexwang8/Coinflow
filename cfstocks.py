import datetime
import time
import pandas as pd
import yfinance as yf
import cfstructs as cfs

class Security:
    ticker = ""
    name = ""
    price = 0.0
    sectype = ""
    dateRecorded : datetime.datetime

    def __init__(self, ticker, name, price, sectype, dateRecorded=datetime.datetime(1, 1, 1)):
        self.ticker = ticker
        self.name = name
        self.price = price
        self.sectype = sectype
        self.dateRecorded = dateRecorded

    def __str__(self):
        return self.ticker + " " + self.name + " " + str(self.price)

    def __repr__(self):
        return self.ticker + " " + self.name + " " + str(self.price)


#----------------------------------------------------------------------------

def getTickers():
    tickers = list()
    with open('stocks.txt', 'r') as f:
        tickers = f.readlines()
        f.close()
    #each line is a new ticker
    tickers = [x.strip() for x in tickers]
    return tickers

def getData():
    tickersList = getTickers()
    #add snp500, nasdaq, and dow
    indexes = ["^GSPC", "^IXIC", "^DJI"]
    tickersList = tickersList + indexes
    tickersList = list(set(tickersList))
    tickerStr = ' '.join(tickersList)
    cdate = time.strftime("%Y-%m-%d")
    cfs.Logger().log(f"Grabbing data for {len(tickersList)} tickers...", 'INFO')
    tickers = yf.Tickers(tickerStr)

    # init dict
    tickersDict = {}
    for ticker in tickersList:
        #get close, open, high low, date(unix) over last 3mo
        closePrices = tickers.tickers[ticker].history(period="3mo")['Close']
        openPrices = tickers.tickers[ticker].history(period="3mo")['Open']
        highPrices = tickers.tickers[ticker].history(period="3mo")['High']
        lowPrices = tickers.tickers[ticker].history(period="3mo")['Low']
        dates = tickers.tickers[ticker].history(period="3mo").index
        datesAsUnix = list()
        for d in dates:
            datesAsUnix.append(d.timestamp())

        if len(closePrices) == 0:
            cfs.Logger().log("No data for " + ticker, 'INFO')
            continue
            
        #get the latest close price
        tickersDict[ticker] = (datesAsUnix, closePrices, openPrices, highPrices, lowPrices)


    # verify data present and remove empty keys
    #CleanedTickersDict = {}
    #for ticker in tickersDict:
    #    if tickersDict[ticker]:
    #        cfs.Logger().log(f"{ticker}: {tickersDict[ticker]}")
    #        CleanedTickersDict[ticker] = tickersDict[ticker]
    #    else:
    #        cfs.Logger().log("No data for " + ticker, 'INFO')
    
        
    #convert pandas series to list
    for ticker in tickersDict:
        close = tickersDict[ticker][1].tolist()
        open = tickersDict[ticker][2].tolist()
        high = tickersDict[ticker][3].tolist()
        low = tickersDict[ticker][4].tolist()
        tickersDict[ticker] = (tickersDict[ticker][0], close, open, high, low)

    #print(tickersDict)
    #for ticker in tickersDict:
    #    print(type(tickersDict[ticker][0]))
    #    print(type(tickersDict[ticker][1]))
    #    print(type(tickersDict[ticker][2]))
    #    print(type(tickersDict[ticker][3]))
    #    print(type(tickersDict[ticker][4]))
        
    cfs.Logger().log(f"Done grabbing data for {len(tickersDict)} tickers!", 'INFO')
    return tickersDict, tickersList
 
if __name__ == '__main__':
    getData()
