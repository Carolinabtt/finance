import numpy as np
import pandas as pd
import investpy
import matplotlib.pyplot as mplt
import seaborn as sbn
import datetime
sbn.set(rc={'figure.figsize':(10, 5)})

# https://unipython.com/analisis-de-series-temporales-con-la-libreria-pandas/
pd.to_datetime(['18/07/19','9/8/93','15/12/03'], format='%d/%m/%y')

# Lectura de datos historicos con indice por dia
fondos_dia = pd.read_csv('fondos_esp_2017_2020.csv',
            index_col=['Date','Fondo','Currency'],
            parse_dates=True)
fondos_dia = pd.read_csv('fondos_esp_2017_2020.csv', index_col=0, parse_dates=True)
fondos_dia.index

fondos_dia[fondos_dia.index.duplicated()]
fondos_dia = fondos_dia[~fondos_dia.index.duplicated()]
len(fondos_dia)
fondos_dia['Año'] = fondos_dia.index.year
fondos_dia['Mes'] = fondos_dia.index.month
fondos_dia['Dia'] = fondos_dia.index.day
#fondos_dia['Dia'] = fondos_dia.index.weekday_name
fondos_dia = fondos_dia.drop_duplicates(subset=['Fondo','Open','High','Low','Close'], keep='last')

# Frecuencias
muestra = pd.date_range('2017-01-31','2020-07-31',freq='M')
#muestra = pd.to_datetime(['2018-04-04','2018-12-31','2019-12-31','2020-07-31'])
fondos_dia.reindex(muestra)
fondos_mes = fondos_dia.loc[fondos_dia.index.intersection(muestra),['Close']].copy()
fondos_mes = fondos_mes.drop_duplicates(subset='Close', keep='last')

# Datos con valores de meses completos
freq_fondos = fondos_dia.asfreq('M')
freq_fondos['Close - Datos llenos'] = fondos_dia.asfreq('M', method='ffill') # metodo llenado hacia adenate

len(fondos_mes)
fondos_mes.to_csv('fondos_esp_2017_2020_M.csv')
#fondos_mes['Fondo']=='Natbry Inversiones Sicav S.a.'
#fondos_inifin = fondos_mes.groupby('Fondo')['Date'].aggregate(Date_ini ="min", Date_fin="max")
#inicio = caracteristicas.filter(created=fecha_antigua)

# Remuestreo
columnas = ['Fondo','Close']
media_opsd_semanal = opsd_dia[columnas].resample('W').mean()
media_opsd_semanal.head(3)

# Filtro de un fondo
in_fondo1=fondos_dia['Fondo']=='Morgan Stanley Investment Funds - Us Growth Fund A'
fondo1=fondos_dia[in_fondo1]
fondo1.drop_duplicates(subset='Close', keep='last')

# Selecciono todo un mes o todo un año
fondos_dia.loc['2020-01-15':'2020-02-20']
fondos_dia.loc['2020-03']
fondo1.loc['2020']

# Grafico
fondo1['Close'].plot(linewidth=0.1)

col_graf = ['Close']
ejes = fondo1[col_graf].plot(marker='.', alpha=0.1, linestyle='None',figsize=(10,10),subplots=True)
for eje in ejes:
  eje.set_ylabel('Precio Cierre del dia')

# Box plot
fig, ejes = mplt.subplots(2, 1, figsize=(11, 10), sharex=True)
for nombre, eje in zip(['Open','Close'], ejes):
    sbn.boxplot(data=fondo1,x='Mes',y=nombre,ax=eje)
    eje.set_title(nombre)
    if eje != ejes[-1]:
        eje.set_xlabel('')

# Boxplot Por dia de la semana
sbn.boxplot(data=fondo1, x='Mes', y='Close')
