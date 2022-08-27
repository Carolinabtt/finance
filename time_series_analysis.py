# %% codecell
import numpy as np
import pandas as pd
import pandas_datareader as dr
import matplotlib.pyplot as plt
from datetime import date
import yfinance as yf
import pyEX as p
from bs4 import BeautifulSoup as bs
from pandas_datareader import data
from yahoofinancials import YahooFinancials
import requests
import json
import sys
from enum import Enum
#from urllib import urlopen
from lxml.html import parse
import requests
# %% codecell

# Read excel with total companies symbols (tickers)
stocks = pd.read_excel('Tickers.xlsx', sheet_name="Tickers")
stocks = stocks['Symbol']
sector = stocks.iloc[:,[0,3,6,7]].set_index('Symbol')
stocks = stocks.drop_duplicates()
tickers = stocks.values.tolist()
tickers = tickers[11:16]
thelen = len(tickers)
thelen

# Collecting companies Sector and Industry from yahoofinance website
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

# analysis of stock between a period of time
Activo = 'SPY'
FechaInicio = ' 01-01-2020'
FechaFinal =  '16-11-2020'
timeframe = '1y'

df = dr.data.get_data_yahoo(Activo, start=FechaInicio, end=FechaFinal)
df = df[~df.index.duplicated()]
df.tail()
df=df.iloc[:,[5]]
df.reset_index(level=0, inplace=True)
df.columns=['ds','y']

# Cambio porcentual de la serie de precios
df["R.Aritmetico"] = df["Adj Close"].pct_change()
df["R.Logarit"] = np.log(df["Adj Close"]) - np.log(df["Adj Close"].shift(1)) # es muy silimar al aritmetico
df.tail()
df.head()

exp1 = df.y.ewm(span=20, adjust=False).mean()
exp2 = df.y.ewm(span=50, adjust=False).mean()

plt.plot(df.ds, df.y, label='AMD')
plt.plot(df.ds, exp1, label='AMD 20 Day EMA')
plt.plot(df.ds, exp2, label='AMD 50 Day EMA')
plt.legend(loc='upper left')
plt.show()

# Graficos de variacion de precios
import seaborn as sns
import scipy.misc
from scipy.stats import norm
from scipy import stats

#Elimino primera fila
df = df.iloc[1:]

# Histograma de Frecuencias
plt.figure(figsize=(15,8))
sns.set(color_codes= True)
ax = sns.distplot(df["R.Aritmetico"], bins=100, kde=False,
     fit=stats.norm, color='green')

# Obtenemos los parametros
(mu, sigma)= stats.norm.fit(df["R.Aritmetico"])

plt.title("Distribucion historica de retornos diarios", fontsize=16)
plt.ylabel("Frecuencia")
plt.legend(["Distribucion normal. fit ($\mu=${0:.2g}, $\sigma=${1:.2f})". format(mu, sigma),
"Distibucion R. Aritmeticos"] )

# Estadistica descriptiva
años = df["R.Aritmetico"].count()/252
CAGR = (df['Adj Close'].iloc[-1]/df['Adj Close'].iloc[0])**(1-años) -1

# Variacion vs Maximo
Maximo_anterior = df['Adj Close'].cumax()
drawdowns = 100*((df['Adj Close'] - Maximo_anterior)/ Maximo_anterior)
DD = pd.DataFrame({'Adj Close': df['Adj Close'],
            'Previous Peak': Maximo_anterior,
            'Drawdown' : drawdowns})

# Asimetria y curtosis
# VaR teorico
print('>Var Modelo Gaussiano MC-95% :', '%.6s' % (100 * norm.ppf(0.05, mu, sigma)), '%' )
print('>Var Modelo Gaussiano MC-99% :', '%.6s' % (100 * norm.ppf(0.01, mu, sigma)), '%' )

# VaR real historico
print('>Var Modelo Real MC-95% :', '%.6s' % (100 * np.percentile(df['R.Aritmetico'],5)), '%' )
print('>Var Modelo Real MC-99% :', '%.6s' % (100 * np.percentile(df['R.Aritmetico'],1)), '%' )
var95 = np.percentile(df['R.Aritmetico'],5)
var99 = np.percentile(df['R.Aritmetico'],1)

# Volatilidad
df['Volat_Hist_14d'] = 100*df['R.Aritmetico'].rolling(14).std()
df['Volat_Hist_14d_Anualiz'] =  df['Volat_Hist_14d']*(252**0.5)
df['SMA_126_Volat_Anualiz'] = df['Volat_Hist_14d_Anualiz'].rolling(126).mean()
df.tail()

fig, ax1 = plt.subplots(figsize=(15,8))
ax2 = ax1.twinx()
volatilidad = ax1.plot(df['Volat_Hist_14d_Anualiz'] ,'orange', linestyle='--', label = 'Vol 14d anualiz')
smaLine = ax1.plot(df['SMA_126_Volat_Anualiz'], 'green', linestyle='-', label = 'SMA 126 Vol anualiz')
adjustedCloseLine = ax2.plot(df['Adj Close'], 'black', label='Precio de cierre ajustado')

# Volatilidad anualizada
VMA = (252 **0.5)*(100*df['R.Aritmetico'].std())
print('Volatilidad anualizada:' , '%.6s' % VMA, '%')

# Volatilidad maxima y minima
Fecha_Min_Volat = df.Volatilidad_14_Dias_Anualiz[df.Volatilidad_14_Dias_Anualiz ==
            df['Volatilidad_14_Dias_Anualiz'].min()].index.strftime('%Y-%m-%d').tolist()
Fecha_Max_Volat = df.Volatilidad_14_Dias_Anualiz[df.Volatilidad_14_Dias_Anualiz ==
            df['Volatilidad_14_Dias_Anualiz'].max()].index.strftime('%Y-%m-%d').tolist()
