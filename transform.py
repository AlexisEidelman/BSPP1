# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 23:41:51 2015

@author: alexis

Transforme les donneés, en séparant les infos propres à 
l'ntervention, celles propres aux véhicules et celles qui 
décrivent le déroulé de l'intrevention

on travaille ensuite avec le début de l'intervention

Ensuite, un exemple sur les motifs, donne la répartition des 
interventions, par heures, à ce niveau là, on a une colonne
par type d'intervention.
"""

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

from read import read

tab = read()

## crée une table avec la définition des intervention
id = ['id_intervention']
def_interevention = ['zone', 'motif_ini', 'motif']
intervention = tab[id + def_interevention]
grouped = intervention.groupby(id)
assert all(grouped.agg(lambda x: len(np.unique(x))) == 1)
intervention = grouped.first()

tab.drop(def_interevention, axis=1, inplace=True)
# => 41909 interventions

## crée une table avec la définition des véhicule
id = ['id_vehicule']
def_vehicule = ['type_ini', 'zone_ini']
vehicule = tab[id + def_vehicule]
grouped = vehicule.groupby(id)
assert all(grouped.agg(lambda x: len(np.unique(x))) == 1)
vehicule = grouped.first()

tab.drop(def_vehicule, axis=1, inplace=True)
# => 1031 véhicules


# début de l'intervention
tab['date'] = tab.index
debut = tab.groupby(['id_intervention'])['date'].min()
debut = pd.DataFrame(debut)
debut.reset_index(inplace=True)
debut.set_index(pd.DatetimeIndex(debut['date']), inplace=True)
del debut['date']


# transforme les dates en tranche de dix
deb = debut.merge(intervention, left_on='id_intervention', right_index=True)

# on retire le premier janvier mais on pourrait ne pas le faire
deb = deb['2015-01-02':]

def reshape(var, limite):
    ''' crée une variable par valeur de la colonne var
        a été ecrit initialement avec var = zone
        la limite c'est pour selectionner les éléments significatifs
    '''
    zone = pd.get_dummies(deb[var], prefix='')
    ## on séléctionne les éventement à plus de 50 incidents
    _sum = zone.sum()
    to_keep = _sum[_sum > limite].index
    zone = zone[to_keep]
    zone = 100*zone/zone.sum()
    return zone
    
zone = reshape('zone', 100)
zone.resample('1D', how=np.sum).iloc[:, :10].plot()

motif = reshape('motif', 100)
motif.columns = [x[1:-2] for x in motif.columns]
motif.resample('H', how=np.sum).iloc[:, :10].plot()
motif_h = motif.resample('H', how=np.sum)
motif_h['hour'] = motif_h.index.hour
motif_by_hour = motif_h.groupby('hour').sum()
motif_by_hour.plot()

#gp_zone = deb.groupby('zone')
#
#
#def print_el_in_group(group):
#    for name, values in group.groups.iteritems():        
#        size = len(values)
#        label = 'groupe ' + str(name) + ', taille ' + str(size)
#        if size > 5:
#            serie.plot(label= label, legend=True)
#        else:
#            label = 'groupe ' + str(n_group)
#            serie.plot(label= label, legend=True)
#
#print_el_in_group(gp_zone)
#
#unik = deb.resample('10Min', how=np.count_nonzero)
#
#dates = matplotlib.dates.date2num(values)
#plt.plot_date(dates, values)
#
## TODO: pivot table
#xx
##def select_categ(zone=None, motif_ini=None, motif=None):
##    
#
#test.groupby([pd.Grouper(freq='10')]).mean()
#
#test.asfreq('10min', method='pad')
#
#test = tab[tab['motif'].isin(range(500, 510))]