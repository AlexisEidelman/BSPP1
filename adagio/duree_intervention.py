# -*- coding: cp1252 -*-
"""
@author: aeidemlan
"""
import datetime
import pandas as pd

from read import read_bspp_table, read_configuration
from tools import translate_id_into_label

tab = read_bspp_table("GestionMMA_HistoriqueMMAStatutOperationnel",
                      skiprows=5000, nrows = 100000,
                      usecols=[1,2,4,5])
# 'IdMMASelection' joue le rôle de numéro d'intervention par
# véhicule
                      
tab['date'] = pd.to_datetime(tab['DateStatutOperationnelMMA'],
                      format='%Y-%m-%d %H:%M:%S')
del tab['DateStatutOperationnelMMA']
tab['date'].value_counts() #beaucoup de date à la millisecondes prises
# plusieurs fois.
# C'est moins le cas quand on fait tab[test > '2013']
# tab[test > '2013'].DateStatutOperationnelMMA.value_counts()
#=> on peut imaginer qu'il y a eu une correction avant 2013         
print(tab.date.dt.year.value_counts())

def voir_intervention(num_intervention, from_table=tab):
    ''' pour facilement voir une intervention '''
    tab = from_table[from_table['IdMMASelection'] == num_intervention]
    return tab.sort_values('date')


statut_op = read_configuration('StatutOperationnel')
tab = translate_id_into_label('StatutOperationnel', 
                              tab, statut_op, method='merge')
#
# sit on veut d'autres infos de StatutOperationnel
#tab = tab.merge(statut_op[['IdStatutOperationnel', 'LibelleStatutOperationnel', 'Disponibilite']])
#del tab['IdStatutOperationnel']
tab.rename(columns={
    'StatutOperationnel':'statut',
    }, inplace=True)
#tab['Disponibilite'].astype(bool)

print(voir_intervention('884767'))

var_utiles =  ['IdMMA','statut','date', 'IdMMASelection']
utiles = tab[tab['IdMMASelection'] > '0']
# TODO: comprendre ce que c'est quand pas d'intervention

# on a des doublons
len(utiles) == len(utiles.drop_duplicates(['IdMMA', 'IdMMASelection', 'statut']))
# => on fait les bourrins : on retire les interventions concernées
# TODO: faire mieux
avec_doublons = utiles[utiles.duplicated(['IdMMA', 'IdMMASelection', 'statut'])]['IdMMASelection']
utiles = utiles[~utiles['IdMMASelection'].isin(avec_doublons.unique())]

bon_format = utiles[var_utiles].set_index(['IdMMA', 'IdMMASelection', 'statut']).unstack()
bon_format.columns = bon_format.columns.levels[1]
bon_format.isnull().sum()



## prépare un modèle de regression
statut_d_une_intervention_classique = [
    'Instance de sélection',
    'Sélection',
    'Instance départ',
    'Parti',
    'Sur les lieux ',
    'Transport hôpital',
    'Arrivée hôpital',
    'Quitte hôpital',
    'Indisponible Montée en GARDE',
    'Indisponible en Transit',
    # disponible
    'Rentré',
    'Disponible',
    ]
# tous les autres c'est indisponible


### on crée maintenant les variables utiles pour la régression.
# on selectionnce uniquement quand on a rempli la liste suivante
var_hopital = ['Transport hôpital','Arrivée hôpital','Quitte hôpital']
bon_format['hopital'] = bon_format[var_hopital].notnull().sum(1) > 0


statut_obligatoire = [
    'Instance départ',
    'Parti',
    'Sur les lieux',
    # disponible
    'Rentré',
    'Disponible',
    ]
cond_tout_rempli = bon_format[statut_obligatoire].isnull().sum(1) == 0
tout_rempli = bon_format.loc[cond_tout_rempli, statut_obligatoire + ['hopital']]
# => on retire un tiers des intervention

tout_rempli.reset_index(inplace=True)

#####  les infos sur le MMA ######
mma = read_configuration('MMA')
# on utilise pas l'originel
del mma['IdFamilleMMAOriginelle']
# TODO: retirer d'autres variables
#TODO savoir ce qu'est un Omnibus
to_remove = ['ImmatriculationBSPPMMA', 'ImmatriculationAdministrativeMMA', 
             'RFGI', 'GSM', 'Actif', 'Strada', 'Libelle_GTA', 'Omnibus',
             'Associe', 'OrdreGTA', 'Disponible', 'Observation',
             'IdStatutOperationnel']
mma.drop(to_remove, axis=1, inplace=True)

# famille mma
famille_mma = read_configuration('FamilleMMA')
del famille_mma['FamilleMMA'] # qui est vide
mma.rename(columns={'IdFamilleMMAOperationnelle': 'IdFamilleMMA'}, inplace=True)
mma = translate_id_into_label('FamilleMMA', 
                              mma, famille_mma, method='merge')
        
                              
var_nombre = [var for var in famille_mma.columns if 'Nombre' in var]
famille_mma = famille_mma[['LibelleFamilleMMA'] + var_nombre]
mma = mma.merge(famille_mma, left_on='FamilleMMA', right_on='LibelleFamilleMMA')
del mma['LibelleFamilleMMA']

# Apparentance
appartenance = read_configuration('MoyenSecoursAppartenance')
mma = translate_id_into_label('MoyenSecoursAppartenance',
                              mma, appartenance, method='merge')
                              
#IdFamilleMMAModele
assert all(mma.IdFamilleMMAModele == '1')
# donc variable ininteressante
# donc MMAModele = read_configuration('FamilleMMAModele') ne sert à rien
# donc:
del mma['IdFamilleMMAModele']
# TODO: regarder les autres variables ident
# IdLieuStationnementOperationnel 
# et
# IdAffectationAdministrative
tout_rempli = tout_rempli.merge(mma, on='IdMMA')



#####  les infos sur les interventions ######
# tables concernée
#        "Appel112_MMASelection",
#        "Appel112_MMARessourcePartageeSelection",
#        "GestionMMA_FamilleMMASelection"
selection = read_bspp_table("Appel112_MMASelection", nrows=1000)

xxx
type_selection = read_bspp_table("Appel112_R_TypeSelection")
#   IdTypeSelection AbregeTypeSelection          LibeleTypeSelection
#0                0                   A                       Annulé
#1                1                   D                   Définitive
#etc...
selection = selection.merge(type_selection)
del selection['IdTypeSelection']

resume = read_bspp_table("Appel112_InterventionResume",
                         usecols=[0,1,2,3,4])
selection = selection.merge(resume, on = 'IdIntervention')
# TODO: on a d'autre chose à faire, il faut faire le merge avec
# IdMMA par exemple. En attendant
del selection['IdMMA']
del selection['IdIntervention']


tout_rempli = tout_rempli.merge(selection, on = 'IdMMASelection',
                                how='left')
tout_rempli.rename(columns={
    'Disponible_x':'Disponible',
    }, inplace=True)

# Il ne reste plus qu'à générer des données sur le temps
for statut in statut_obligatoire[1:]:
    tout_rempli[statut + ' duree'] = tout_rempli[statut] - tout_rempli['Instance départ']
    tout_rempli[statut + ' duree s'] = tout_rempli[statut + ' duree'].dt.seconds
    for quart_d_heure in range(8):
        name = statut + ' qt_' + str(quart_d_heure)
        tout_rempli[name] = tout_rempli[statut + ' duree s'] / (60*15*(quart_d_heure + 1)) > 1

tout_rempli['longue duree'] = tout_rempli['Disponible duree s'] > 3600*3




tout_rempli.tail(5).to_csv('bspp_datarobot.csv', index=False)

import numpy as np
tirage = np.random.randint(0, len(tout_rempli), 50000)

from itertools import product
import string

save2 = tout_rempli.copy()

tout_rempli.iloc[tirage].to_csv('bspp_datarobot_random_50000.csv',
 index=False, encoding='utf8')



def numeric_id_to_char_id(col):
    values = tout_rempli[col].astype(int).unique()
    values.sort()
    int_to_char = dict()
    char_values = product(string.ascii_uppercase, repeat=3)
    assert len(values) < 17576 # 26*26*26

    for k in range(len(values)):
        char_value =  next(char_values)
        char_value = ''.join(char_value)
        int_to_char[str(values[k])] = char_value

    return int_to_char


    tout_rempli[col].replace(int_to_char)

int_to_char = numeric_id_to_char_id('IdMMA')
tout_rempli['IdMMA'] = tout_rempli['IdMMA'].replace(int_to_char)

var_label = ['ObservationsPourMMA', 'LibelleMotif', 'LibeleTypeSelection', 'ImmatriculationBSPPMMA',
'LibelleMoyenSecoursAppartenance', 'LibelleFamilleMMA']
for var in var_label:
    tout_rempli[var] = tout_rempli[var].str.replace('é','e')

tout_rempli['heure'] = tout_rempli['Instance départ'].dt.hour

# cette table sert uniquement à passer à IdRessourcePartageeSelection
read_bspp_table("Appel112_MMARessourcePartageeSelection", nrows=10)







#comment identifier un véhicule qui a été utilisé de deux façons ?

famille_mma = read_configuration('FamilleMMA')
# (mma.IdFamilleMMAOriginelle != mma.IdFamilleMMAOperationnelle).value_counts()

info_mma.merge(famille_mma,
               left_on = 'IdFamilleMMAOperationnelle',
               right_on = 'IdFamilleMMA',
               )
















#### Etude sur la base appel112 historiqueIntervention
# TODO: début et fin d'intervention
tab['vaut_7'] = tab.IdStatutIntervention == '7'
tab['7_ou_plus'] = tab.IdStatutIntervention >= '7'
tab.groupby('IdIntervention')['vaut_7'].sum()




#=> on charge pluttôt les données à la fin du fichier
debut = datetime.datetime(2013, 1, 2, 0, 0, 0)
fin = tab['date'].max().to_datetime()

tab_periode = tab.sort_values('date').set_index('date')
tab_periode[debut:fin]

tab_periode.IdStatutOperationnel.value_counts()
statut_interet = '1'
tab_periode['etat'] = tab_periode['IdStatutOperationnel'] == statut_interet

# WARNING: when imported with etat initial use ffill
def smart_resample(group):
    return group.resample('600S').bfill().resample('1H').mean()

# Calcul de la proportion en utilisant la fonction resample
resultat = tab_periode[['etat','IdMMA']].groupby('IdMMA').apply(smart_resample).reset_index()




