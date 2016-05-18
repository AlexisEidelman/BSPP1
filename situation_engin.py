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


# fonction pour la premiere table : dans quel etat est chaque engin a une date et heure donnée
# Le resultat est un dictionnaire qui donne la situation operationnelle de chaque engin
def situation_engin(year, month, day, hour, minute, second):
    tryd = datetime.datetime(year, month, day, hour, minute, second)
    i = bisect.bisect_right(tab['date_time'], tryd)
    liste_engins = tab['Immatriculation'].unique()
    statut_engin = dict((key, []) for key in liste_engins)
    tab_avant_date = tab[0:i]
    for engin in liste_engins:
        if isinstance(engin, str):
            a = list(tab_avant_date[tab['Immatriculation'] == engin]['Abrege_Statut_Operationnel'])
            if a != []:
                statut_engin[engin] = a[-1]
    return statut_engin


# Test
year = 2015
month = 1
day = 22
hour = 14
minute = 23
second = 45
resu = situation_engin(year, month, day, hour, minute, second)





# Nouvelle fonction permettant d'obtenir en output 1 : le statut de chaque engin
# en output 2 : le statut des engins de chaque caserne
# en output 3 : le nombre d'engin disponible pour chaque caserne
def engin_caserne(year, month, day, hour, minute, second):
    tryd = datetime.datetime(year, month, day, hour, minute, second)
    i = bisect.bisect_right(tab['date_time'], tryd)
    liste_engins = tab['Immatriculation'].unique()
    liste_lieu = (tab['Immatriculation'].str.split(pat="_", expand=True))[2].unique()
    statut_engin = dict((key, []) for key in liste_engins)
    caserne_engin_statut = dict((key, []) for key in liste_lieu)
    caserne_engin_dispo = dict((key, []) for key in liste_lieu)
    tab_avant_date = tab[0:i]
    for engin in liste_engins:
        if isinstance(engin, str):
            a = list(tab_avant_date[tab['Immatriculation'] == engin]['Abrege_Statut_Operationnel'])
            if a != []:
                statut_engin[engin] = a[-1]
    for lieu in liste_lieu:
        for engin in liste_engins:
            if (isinstance(engin, str) and isinstance(lieu, str) and (lieu in engin)):
                caserne_engin_statut[lieu].append(statut_engin[engin])
        caserne_engin_dispo[lieu] = caserne_engin_statut[lieu].count('D') 
    return statut_engin, caserne_engin_statut, caserne_engin_dispo

# Test
try_ = engin_caserne(year, month, day, hour, minute, second)



# Le lieu de GTA est le centre de secours (caserne ou lieu prédéfini dans ADAGIO)
# TO DO : quand on aura les données avec la vraie immatriculation, on pourra
# identifier la vraie appartenance de chaque engin à chaque caserne


#### Autres commentaires et essais ####

#je regarde quels sont les lieux d'intervention
from collections import Counter
Counter(tab['lieu_initial'])
tab.lieu_initial.nunique()
tab.lieu_intervention.nunique()


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

