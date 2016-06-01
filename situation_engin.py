# -*- coding: utf-8 -*-
"""
Created on Fri May 13 18:35:35 2016
@author: carrierclement
"""

import numpy as np
import pandas as pd
import bisect
import datetime

# Chemin d'Alexis
path = u'/home/sgmap/data/BSPP/Extraction LCL PAGNIEZ.csv'

# Chemin de Clément
#path = '/Users/carrierclement/Documents/Etalab/BSPP/2015-043-\
Extraction LCL PAGNIEZ.csv'

tab = pd.read_csv(path, sep=',')


# je renomme les variables
tab.columns = ['date_time', 'Id_Intervention', 'Id_Intervention_Motif',
               'Code_Cri', 'lieu_initial', 'lieu_intervention',
               'Immatriculation', 'type_initial', 'type_intervention',
               'Abrege_Statut_Operationnel', 'Statut_Operationnel']



# creation d'un objet date_time pour la date et de l'heure
tab['date_time'] = pd.to_datetime(tab['date_time']
                                  , format='%d/%m/%Y %H:%M:%S')

# Remarque : pour certaines dates, il y a eu plusieurs interventions

# On choisit une certaine période d'étude
year = 2015
month = 1
day = 22
hour = 14
minute = 23
second = 46
exemple_date = datetime.datetime(year, month, day, hour, minute, second)

debut = exemple_date
fin = datetime.datetime(year, month, day + 3,
                        hour, minute, second)

## pandas time serie option
tab.set_index('date_time', inplace=True)
grp = tab.groupby('Immatriculation')

# def _find_init(tab, debut, fin):
# renvoie la liste des situations entre deux dates

# On copie la table initiale
tab_travail = tab[['Immatriculation',
                   'Abrege_Statut_Operationnel']].copy()
tab_travail.sort_index(inplace=True)

# On cherche la situation initiale des véhicules sur la période choisie
tab_before = tab_travail[:debut]
etat_initial = tab_before.groupby('Immatriculation').last()
manquant = list(set(tab.Immatriculation.unique()) - set(etat_initial.index.unique()))
manquant = pd.DataFrame({'Abrege_Statut_Operationnel': ['initial'] * len(manquant)}, index=manquant)

etat_initial = pd.concat([etat_initial,manquant])

etat_initial['date_time'] = debut
etat_initial.reset_index(inplace=True)
etat_initial.set_index('date_time', inplace=True)

tab_periode = tab_travail[debut:fin]
tab_periode = etat_initial.append(tab_periode)

statut_interet = 'R'
tab_periode['etat'] = tab_periode['Abrege_Statut_Operationnel'] == statut_interet
tab_periode['etat'] = tab_periode['etat'].astype(int)


debut_file = tab_periode.index.min().to_datetime()
fin_file = tab_periode.index.max().to_datetime()




# Fonction permettant de ne pas executer deux fois la fonction goupby et spécifiant les intervalles temporels utilisés.
# Le premier permet d'obtenir avec un pas régulier, le statut de chaque véhicule
# Le deuxième permet de redéfinir l'intervalle souhaité pour calculer pour chaque véhicule la proportion du temps passé dans le statut d'intérêt noté : 'statut_interet'

def smart_resample(group):
    return group.resample('1S').ffill().resample('1H')

# Calcul de la proportion en utilisant la fonction resample
resultat = tab_periode.groupby('Immatriculation').apply(smart_resample).reset_index()
resultat['caserne'] = resultat['Immatriculation'].str.split(pat="_", expand=True)[2]


# On ajoute aléatoirement des codes postaux pour la VIZ
post_code = [75001,75002,75003,75004,75005,75006,75007,75008,75009,75010,75011,75012,75013,75014,
             75015,75016,75017,75018,75019,75020,91000,92000,93000,94000]

loca= dict((key, []) for key in list(resultat.caserne.unique()))
for localisation in list(resultat.caserne.unique()):
    loca[localisation] = random.choice(post_code)

post_code_resultat = [0] * len(resultat.index)
for i in resultat.index:
    post_code_resultat[i] = loca[resultat['caserne'][i]]

resultat['post_code_resultat'] = post_code_resultat
# On sauvegarde en csv via : resultat.to_csv("result_by_engin_for_map.csv")


# On peut également s'interesser à la proportion de vehicule dans le statut d'intérêt choisi par caserne. 
resultat_bis = resultat.reset_index().set_index('date_time')
resultat_bis['caserne'] = resultat.reset_index().set_index('date_time').Immatriculation.str.split(pat="_", expand=True)[2]

def pivot_function(group):
    return group.pivot(index='date_time', columns='Immatriculation', values='etat').mean(axis=1)

resultat_bis = resultat_bis.reset_index().groupby('caserne').apply(pivot_function)
# On sauvegarde en csv via : resultat_bis.to_csv("result_by_caserne_for_map.csv")

