# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 19:40:07 2015

@author: alexis
"""

import pandas as pd
import os
from read import read

path = 'D:\data\BSPP\meteo.txt'

tab = pd.read_csv(path)
del tab['FullMetar']
del tab['HeureCET']

tab.dropna(how='all', inplace=True)
header = tab.iloc[0,:]

tab.set_index(pd.DatetimeIndex(tab['DateUTC']), inplace=True)

meteo = tab


## étude 


tab = read()
tab.resample('30min')


# TODO: regarder si quand on a pluie, ou brouillard dans événements,
# la structure des motifs changent