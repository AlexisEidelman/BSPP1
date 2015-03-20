# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 17:27:32 2015

@author: Florian Gauthier
"""

import os
import numpy as np
import pandas as pd

from collections import Counter

from read import read
from read import _rename_bspp_cols
from tools_bspp import zeros_rm

path = 'D:\data\BSPP'

tab = read(path)
tab.columns
tab.index

# Quels sont les motifs avec lesquels on se trompe le plus ?

    ######################
    #   Data Cleaning    #
    ######################

tab[u'motif_ini'].value_counts()
z = tab[u'motif_ini'] == tab[u'motif']
Counter(z)

tab.dtypes

#On convertit toutes les variables en "object"
tab.motif = tab.motif.astype(object)
tab.id_intervention = tab.id_intervention.astype(object)

# On enlève les ".0"
tab["motif"] = tab["motif"].apply(zeros_rm)
tab["motif_ini"] = tab["motif_ini"].apply(zeros_rm) #value error


    ######################
    #    Stats descr     #
    ######################

# Les index pour lesquels il y a une erreur
erreurs = tab.motif_ini != tab.motif
tab['erreur'] = erreurs
t_count_error = tab.groupby(["motif_ini","motif"])['erreur'].sum()
t_count_error.sort(ascending=False)
t_count_error

tab.head()

    ########################################
    #    Durées moyenne / intervention     #
    ########################################
# Objectif : calculer la durée d'intervention moyenne par motif

tab['id_intervention'].value_counts()
tab['date'] = tab.index #on récup la date pour simplifier les calculs

group = tab.groupby('id_intervention') 
# TODO : pourquoi ça change quand on groupby motif ? (ah j'ai compris : motif se répètent dans les interventions)
t_duree = group.agg({'date' : [np.min, np.max]})
t_duree = t_duree.reset_index()
t_duree.head()
t_duree['duree'] = t_duree['date']['amax'] - t_duree['date']['amin']

(t_duree['duree'] / np.timedelta64(1,'m')).plot(legend=True)

t_duree['duree'].value_counts()
# 223 interventions à durée nulle.

#TODO : 



# Objectif : 
