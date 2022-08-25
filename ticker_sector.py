# %% codecell
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bs
from pandas_datareader import data
from yahoofinancials import YahooFinancials
import requests
import json
import sys
from lxml.html import parse
import requests
import bs4 as bs
# %% codecell

# en un indice
stocks = pd.read_excel('Tickers.xlsx', sheet_name="TICKERS") # Total Tickers
in_index=stocks['Grupo']=='IBEX35_y'
in_index=stocks['Grupo']!=='IBEX35'
stocks = stocks[in_index]

# Total synmbols
stocks = pd.read_excel('Tickers.xlsx', sheet_name="TICKERS") # Total Tickers
stocks = stocks['Symbol']
sector = stocks.iloc[:,[0,3,6,7]].set_index('Symbol')
stocks = stocks.drop_duplicates()
tickers = stocks.values.tolist()
tickers = tickers[11:16]
thelen = len(tickers)

ticker_sector = pd.DataFrame(columns=['Symbol','Sector','Industry'])
for ticker in range(thelen):
    try:
        url = ("https://finance.yahoo.com/quote/"+tickers[ticker]+"/profile?p="+tickers[ticker])
        r = requests.get(url, timeout=10).text
        soup = bs(r,'html.parser')
        sector_t = soup.findAll('span', {'class': ["Fw(600)"], 'data-reactid': ['23']}) #Sector
        industry = soup.findAll('span', {'class': ["Fw(600)"], 'data-reactid': ['27']}) #Industry
        ticker_sector1 = pd.DataFrame([[ tickers[ticker] , sector_t[0].text, industry[0].text ]], columns=['Symbol','Sector','Industry'])
        ticker_sector= pd.concat([ticker_sector, ticker_sector1] , sort=True)
        print(tickers[ticker], "ok")
    except:
        print(tickers[ticker], 'Error:', sys.exc_info()[0])
        pass

ticker_sector.to_excel('tickers_sector.xlsx')

#### Sector S5P500  solo tiene Sector y Sub-Industry
resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
soup = bs.BeautifulSoup(resp.text, 'lxml')
table = soup.find('table', {'class': 'wikitable sortable'})
print(table)


tickers = []
industries = []
for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        #fourth element is the sector
        industry = row.findAll('td')[4].text

        tickers.append(ticker)
        industries.append(industry)

tickers = list(map(lambda s: s.strip(), tickers))
industries = list(map(lambda s: s.strip(), industries))


tickerdf = pd.DataFrame(tickers,columns=['ticker'])
sectordf = pd.DataFrame(industries,columns=['industry'])

tickerandsector = pd.concat([tickerdf, sectordf], axis=1, join_axes=[tickerdf.index])
print(tickerandsector)
