# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 17:27:32 2015

@author: Florian Gauthier
"""

import pandas as pd
import os

path = 'D:\data\BSPP'
main_file = os.path.join(path, '2015-043-Extraction LCL PAGNIEZ.csv')

tab = pd.read_csv(main_file, sep=',', encoding='utf8')

# Quels sont les motifs avec lesquels on se trompe le plus ?

from collections import Counter

tab[u'Id_Intervention_Abrege_Motif'].value_counts()
z = tab[u'Id_Intervention_Abrege_Motif'] == tab[u'Code_Cri']
Counter(z)

tab = pd.DataFrame(tab)
tab.dtypes

#On convertit toutes les variables en "object"
tab.Code_Cri = tab.Code_Cri.astype(object)
tab.Id_Intervention = tab.Id_Intervention.astype(object)

# on enlève les ".0"
def zeros_rm(i):
    return "%g" % float(i)


tab["Code_Cri"] = tab["Code_Cri"].apply(zeros_rm)
tab["Id_Intervention_Abrege_Motif"] = tab["Id_Intervention_Abrege_Motif"].apply(zeros_rm)

# Les index pour lesquels il y a une erreur
erreurs = tab.Id_Intervention_Abrege_Motif != tab.Code_Cri
tab['erreur'] = erreurs
tab.groupby("Id_Intervention_Abrege_Motif")['erreur'].sum()

tab.groupby(['Id_Intervention_Abrege_Motif', 'Code_Cri']).size()

