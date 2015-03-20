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
# Objectif : calculer la durée d'intervention moyenne par motif moyenne

tab[u'motif_ini'].value_counts()
z = tab[u'motif_ini'] == tab[u'motif']
Counter(z)

tab = pd.DataFrame(tab)
tab.dtypes

#On convertit toutes les variables en "object"
tab.motif = tab.motif.astype(object)
tab.id_intervention = tab.id_intervention.astype(object)

# On enlève les ".0"
tab["motif"] = tab["motif"].apply(zeros_rm)
tab["motif_ini"] = tab["motif_ini"].apply(zeros_rm) #value error

# Les index pour lesquels il y a une erreur
erreurs = tab.motif_ini != tab.motif
tab['erreur'] = erreurs
tab.groupby("motif")['erreur'].sum()

tab.groupby(['motif', 'motif']).size()


# Objectif : 
