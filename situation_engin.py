# -*- coding: utf-8 -*-
"""
Created on Fri May 13 18:35:35 2016

@author: carrierclement
"""

import pandas as pd
import bisect
import datetime
# import os
# import itertools
path = u'/home/sgmap/data/BSPP/Extraction LCL PAGNIEZ.csv'

tab = pd.read_csv(path, sep=',')


# je renomme les variables
tab.columns = ['date_time', 'Id_Intervention', 'Id_Intervention_Motif',
               'Code_Cri', 'lieu_initial', 'lieu_intervention',
               'Immatriculation', 'type_initial', 'type_intervention',
               'Abrege_Statut_Operationnel', 'Statut_Operationnel']



# creation d'un objet date_time pour la date et de l'heure
tab['date_time'] = pd.to_datetime(tab['date_time']
    , format='%d/%m/%Y %H:%M:%S')


#je regarde quels sont les lieux d'intervention
from collections import Counter
Counter(tab['lieu_initial'])
tab.lieu_initial.nunique()
tab.lieu_intervention.nunique()

# use lise
lieux_intervention = tab.lieu_intervention.unique().tolist()
lieux_initiaux = tab.lieu_initial.unique().tolist()

lieu_intervention_not_in_lieu_initial = [x for x in lieux_intervention
    if x not in lieux_initiaux]
print(lieu_intervention_not_in_lieu_initial)

""" CCT CDS2 POUC CASJ CASS nan EMGAS sont les lieux d'interventions
qui ne possedent pas de brigade """



# je regarde les immatriculations (qui ne sont pas les vraies dans ce fichier)
len(tab.Immatriculation.unique())
tab.head(20)


# fonction pour la premiere table : dans quel etat est chaque engin a une date et heure donnée
# Le resultat est un dictionnaire qui donne la situation operationnelle de chaque engin
def situation_engin(year, month, day, hour, minute, second):
    tryd = datetime.datetime(year, month, day, hour, minute, second)
    i = bisect.bisect_right(tab['date_time'], tryd)
    engin = tab['Immatriculation'].unique()
    situation = dict()
    for j in engin:
        situation[j] = tab[0:i][tab['Immatriculation'] == j]['Abrege_Statut_Operationnel'].tail(1)
    return situation

# Test
year = 2015
month = 1
day = 2
hour = 14
minute = 23
second = 45
resu=situation_engin(year, month, day, hour, minute, second)
