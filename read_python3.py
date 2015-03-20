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
# Quels sont les motifs avec lesquels on se trompe le plus ?

tab[u'Id_Intervention_Abrege_Motif'].value_counts()
z = tab[u'Id_Intervention_Abrege_Motif'] == tab[u'Code_Cri']
Counter(z)

tab = pd.DataFrame(tab)
tab.dtypes

#On convertit toutes les variables en "object"
tab.Code_Cri = tab.Code_Cri.astype(object)
tab.Id_Intervention = tab.Id_Intervention.astype(object)

# On enlève les ".0"
tab["Code_Cri"] = tab["Code_Cri"].apply(zeros_rm)
tab["Id_Intervention_Abrege_Motif"] = tab["Id_Intervention_Abrege_Motif"].apply(zeros_rm)

# Les index pour lesquels il y a une erreur
erreurs = tab.Id_Intervention_Abrege_Motif != tab.Code_Cri
tab['erreur'] = erreurs
tab.groupby("Id_Intervention_Abrege_Motif")['erreur'].sum()

tab.groupby(['Id_Intervention_Abrege_Motif', 'Code_Cri']).size()


# Objectif : 
