# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 19:40:07 2015

@author: alexis
"""

import pandas as pd
import os
from read import read
import itertools
path = 'D:\data\BSPP\meteo.txt'

tab = pd.read_csv(path)
del tab['FullMetar']
del tab['HeureCET']

tab.dropna(how='all', inplace=True)
header = tab.iloc[0,:]

tab.set_index(pd.DatetimeIndex(tab['DateUTC']), inplace=True)

meteo = tab


if __name__ == '__main__':
    from transform import motif
    import numpy as np
    mot = motif.resample('30min', how=np.sum)

    met = meteo.iloc[:,[10,12]]
    met.columns = ['conditions', 'date']
    met = met.drop_duplicates(subset=['date'])
    test = mot.merge(met, left_index=True, right_index=True, how='left')
    test['duree'] = 1
    by_condition = test.groupby('conditions').sum()
    duree = 100*by_condition['duree'] / by_condition['duree'].sum()
    final = by_condition.divide(duree, axis=0)
    final['duree'] = duree

    final_see = final[final['duree'] > 5]
    test = test[]



meteo_short = meteo.iloc[:,[4,10,12]]
meteo_short.columns = ['visibilite', 'conditions', 'date']
meteo_short[meteo_short['visibilite']==-9999.0]
meteo_short.conditions.value_counts()

#On essaye de corriger la visibilité

meteo_short['visibilite_shift_av'] = meteo_short.visibilite.shift(1)
meteo_short['visibilite_shift_av2'] = meteo_short.visibilite.shift(2)
meteo_short['visibilite_shift_ap'] = meteo_short.visibilite.shift(-1)
meteo_short['visibilite_shift_ap2'] = meteo_short.visibilite.shift(-2)

compared = pd.concat([meteo_short['visibilite_shift_av'], meteo_short['visibilite']], axis=1)


#    for index, row in meteo_short.iterrows():
#        if row['visibilite'] == -9999.0:
#            row['visibilite'] = row['visibilite_shift_av']
#            if row['visibilite_shift_av'] != -9999.0:
#                row['visibilite'] = row['visibilite_shift_av']
#            elif row['visibilite_shift_ap'] != -9999.0:
#                row['visibilite'] = row['visibilite_shift_ap']
#            else:
#                print('fuck')

def visibilite_change(row, row_av, row_ap, row_av2, row_ap2):
        if row == -9999.0:
            if row_av != -9999.0:
                return row_av
            elif row_ap != -9999.0:
                return row_ap
            elif row_av2 != -9999.0:
                return row_av2
            else:
                return row_ap2
        else:
            return row

meteo_short.loc[meteo_short.visibilite== -9999, 'visibilite'] = \
    meteo_short.loc[meteo_short.visibilite== -9999, 'visibilite_shift_av']

meteo_short.loc[meteo_short.visibilite== -9999, 'visibilite'] = \
    meteo_short.loc[meteo_short.visibilite== -9999, 'visibilite_shift_ap']
    
assert all(meteo_short.visibilite != -9999)

tab = meteo_short
tab.replace(-9999.0, np.nan)
tab.fillna(how='bfill', axis=0)

row_1 = row[0]
assert row[0] != -9999
for row in row['visibilite']:
    if row == -9999:
        row = row_1
    row_1 = row

meteo_short['visibilite'] = meteo_short.apply(lambda row: visibilite_change(row['visibilite'], row['visibilite_shift_av'], row['visibilite_shift_ap'], row['visibilite_shift_av2'], row['visibilite_shift_ap2']),
                  axis=1) #Ne fonctionne pas


## étude

tab = read()

import datetime
def round_to_30min(t):
    delta = datetime.timedelta(minutes=t.minute%30,
                               seconds=t.second,
                               microseconds=t.microsecond)
    t = t - delta
    if delta > datetime.timedelta(0):
        t = t + datetime.timedelta(minutes=30)
    return t



tab['date'] = tab.index.map(round_to_30min)

ns30min=30*60*1000000000   # 30 minutes en nano-secondes
tab['date'] = pd.DatetimeIndex(((tab.index.astype(np.int64) // ns30min + 1 ) * ns30min))

tab.resample('30min')



# TODO: regarder si quand on a pluie, ou brouillard dans événements,
# la structure des motifs changent