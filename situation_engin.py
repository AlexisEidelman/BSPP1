# -*- coding: utf-8 -*-
"""
Created on Fri May 13 18:35:35 2016

@author: carrierclement
"""

import numpy as np
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
#def situation_engin(date):
#    assert isinstance(date, datetime.datetime)
#    i = bisect.bisect_right(tab['date_time'], date)
#    liste_engins = tab['Immatriculation'].unique()
#    statut_engin = dict((key, []) for key in liste_engins)
#    tab_avant_date = tab[0:i]
#    for engin in liste_engins:
#        if engin == str('nan'):
#            next
#        a = list(tab_avant_date.loc[tab['Immatriculation'] == engin, 'Abrege_Statut_Operationnel'])
#        # assert isinstance(engin, str)
#        if a != []:
#            statut_engin[engin] = a[-1]
#    return statut_engin


# Test
year = 2015
month = 1
day = 22
hour = 14
minute = 23
second = 46
exemple_date = datetime.datetime(year, month, day, hour, minute, second)
#resu = situation_engin(exemple_date)

debut = exemple_date
fin = datetime.datetime(year, month, day + 3,
                        hour, minute, second)

## pandas time serie option
tab.set_index('date_time', inplace=True)
grp = tab.groupby('Immatriculation')

#def _find_init(tab, debut, fin):
#    '''renvoie la liste des situations entre deux dates '''
tab_travail = tab[['Immatriculation', 
                  'Abrege_Statut_Operationnel']].copy()
tab_travail.sort_index(inplace=True)

tab_before = tab_travail[:debut]
etat_initial = tab_before.groupby('Immatriculation').last()


etat_initial['date_time'] = debut
etat_initial.reset_index(inplace=True)
etat_initial.set_index('date_time', inplace=True)
# TODO: add immatriculation with no event before debut

tab_periode = tab_travail[debut:fin]
tab_periode = tab_periode.append(etat_initial)

tab_periode['etat'] = tab_periode['Abrege_Statut_Operationnel'] == 'R'


# les stats que l'on veut
# nombre de fois que le status est pris
tab_periode.groupby('Immatriculation')['etat'].sum()

# temps moyen où le véhicule est dans l'état
# TODO: rolling mean in pandas
def time_mean(group):
    import pdb; pdb.set_trace()
    group.sort_index(inplace=True)
    index = pd.Series(group.index)
    group['duree']
    group['duree'] = (index.shift(-1) - index).values
    group['duree'][-1] = fin - index.iloc[-1]
    try:
        assert group['duree'].sum() == fin - debut
    except:
        import pdb; pdb.set_trace()
    group['duree'] = group['duree'] / np.timedelta64(1,'s')
    return np.average(group.etat, weights=group.duree)

print(tab_periode.groupby('Immatriculation').transform(time_mean))
xxx

# Nouvelle fonction permettant d'obtenir en output 1 : le statut de chaque engin
# en output 2 : le statut des engins de chaque caserne
# en output 3 : le nombre d'engin disponible pour chaque caserne
def engin_caserne(date, statut_demande):
    ''' utilise la fonction precedente et renvoie le nombre de vehicule en statut_demande  '''
    liste_engins = tab['Immatriculation'].unique()
    liste_lieu = (tab['Immatriculation'].str.split(pat="_", expand=True))[2].unique()
    caserne_engin_statut = dict((key, []) for key in liste_lieu)
    caserne_engin_dispo = dict((key, []) for key in liste_lieu)
    statut_engin = situation_engin(date)
               
    for lieu in liste_lieu:
        for engin in liste_engins:
            if (isinstance(engin, str) and isinstance(lieu, str) and (lieu in engin)):
                caserne_engin_statut[lieu].append(statut_engin[engin])
        caserne_engin_dispo[lieu] = caserne_engin_statut[lieu].count(statut_demande) 
    return statut_engin, caserne_engin_statut, caserne_engin_dispo
# Test
try_ = engin_caserne(exemple_date, 'R')



# Le lieu de GTA est le centre de secours (caserne ou lieu prédéfini dans ADAGIO)
# TO DO : quand on aura les données avec la vraie immatriculation, on pourra
# identifier la vraie appartenance de chaque engin à chaque caserne






# Nouvelle fonction permettant de calculer directement la mateice. 
def situation_engin_bis():
    liste_engins = tab['Immatriculation'].unique()
    print('done')
    liste_date_intervention = tab.index
    # J'initialise le statut des engins comme étant occupé
    statut_engin = dict((key, ['O']) for key in liste_engins)
    for date in liste_date_intervention:
        veh = tab[tab.index == date]
        eng = veh['Immatriculation'][-1]
        val = veh['Abrege_Statut_Operationnel'][-1]
        for key, values in statut_engin.items():
            if key == eng:
                values.append(val)
            else:
                values.append(values[-1])    
    return(statut_engin)
matrice = situation_engin_bis() 






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

