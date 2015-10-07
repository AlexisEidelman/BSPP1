# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 13:59:25 2015

@author: Alexis Eidelman
"""

import pandas as pd
from datetime import timedelta

from BSPP1.read_extract import read

#### PREPARATION DONNÉES APHP ######

# TODO: on court circuite pour ne pas avoir à tout charger à chaque fois
#from APHP.clean_table import import_clean_aphp_pg
#aphp = import_clean_aphp_pg()
#extract_large = aphp.loc['2014-08-01':'2014-08-04']
#extract_large.to_csv('D:\data\BSPP\extract_large.csv', index=False)

extract_large = pd.read_csv('D:\data\BSPP\extract_large.csv')
extract_precis = extract_large[extract_large['mode'] == 'pompier']
aphp = extract_precis

# retire les indicatrices de gravité
indicatrices = [x for x in aphp.columns if x[:12] == 'gravite_lvl_']
to_delete = indicatrices + ['JOUR_ENTREE', 'MOIS_ENTREE', 'ANNEE_ENTREE']
aphp.drop(to_delete, axis=1, inplace=True)
aphp = aphp[['SITE', u'DATE_ENTREE',  u'HPEC_INIT_IAO', 'gravite_lvl',
             u'CODE_POSTAL', u'ANNEE_NAISSANCE', 'age',
             'MODE_ARRIVEE',  u'MOTIFMED1']]

for var in ['DATE_ENTREE', 'HPEC_INIT_IAO']:
    aphp[var].replace('0', '', inplace=True)
    aphp[var] = pd.to_datetime(aphp[var].str.replace('-','/'))

#### PREPARATION DONNÉES BSPP ######

victimes = read('Victimes')
intervention = read('Intervention')
statut = read('Statuts Engins')
engin = read('Engin')

### séléction de victimes dans l'hpital qui va bien
victimes[u'Nom Établissement'].value_counts()
## recode le nom établissement
victimes['hopital'] = ''

traduction_hopital = dict(
    APR = 'HOPITAL AMBROISE PARE (AP-HP)',
    BCT = 'HOPITAL BICETRE (AP-HP)',
    TRS = 'GPE HOSP ARMAND TROUSSEAU-ROCHE GUYON',
    LMRA = 'HOPITAL LOUIS MOURIER (AP-HP)'
    )

for nom, nom_init in traduction_hopital.iteritems():
    victimes.loc[victimes[u'Nom Établissement'] == nom_init, 'hopital'] = nom

bspp = victimes[victimes['hopital'] != '']

### merge avec statut arrivée hopital
arrivee_hop = statut[u'Id Statut Operationnel Libelle Statut Operationnel'] == u'Arrivée hôpital'
statut = statut[arrivee_hop]
test = bspp.merge(statut, how='left', right_on=u'Id Intervention',
                  left_on=u'ID202 Numéro Intervention')
## il n'y a pas toujours l'arrivée à l'hopital de renseigner, on tente un truc plus général
# et on se servira de l'info si nécessaire plus tard
bspp = bspp.merge(engin, how='left')


var_to_keep = [u'ID202 Numéro Intervention', u'ID255 Numéro de victime',
               'hopital', 'CS Affectation', u'ID262 Code Transport',
               u'ID261 Code Soin', u'ID260 libellé Affection',
               u'ID259 Identification', 'age']

why_not = [u'ID267 Code Destination', u'ID266 Code Secours Médicaux',
           u'ID265 Code État Départ', u'ID264 Code État Arrivée',
           u'ID263 Code Arrivée Des Secours Médicaux']

dates_bspp = [u'ID244 Instance De Départ', u'ID245 Parti',
              u'ID246 Sur Les Lieux', u'ID537 Départ vers Hopital',
              u'Engins 538 Présentation Hopital', u'ID539 Quitte Hopital',
              u'ID247 Disponible', u'ID248 Rentrée']


for var in dates_bspp:
    try:
        bspp[var].replace('0', '', inplace=True)
        bspp[var] = pd.to_datetime(bspp[var].str.replace('-','/'), dayfirst=True)
    except:
        print('est-ce que cette variable est bien un datetime ? : ' + var)

bspp.rename(columns={u'Age numérique ':'age'}, inplace=True)
bspp = bspp[var_to_keep + dates_bspp]
bspp = bspp[bspp[u'ID262 Code Transport'] == u'Engin rédacteur']


###### MATCHING PROPREMENT DIT #####

# première tentative sur l'horaire de prise en charge
test = bspp[u'Engins 538 Présentation Hopital'].isin(aphp['DATE_ENTREE'])
test = bspp.merge(aphp, left_on=u'Engins 538 Présentation Hopital',
                  right_on = 'DATE_ENTREE', how='inner')



#### en travaillant ligne par ligne
row = bspp.iloc[0, :]
matched_bspp = pd.Series(index = bspp.index)

for idx, row in bspp.iterrows():
    if row[u'ID262 Code Transport'] == u'Engin rédacteur':
        pass
    # on sait qu'il est rentré dans l'hopital entre le début et la fin de
    # l'intervention
    cond_temps = (aphp['DATE_ENTREE'] > row['ID246 Sur Les Lieux']) & \
                 (aphp['DATE_ENTREE'] < row[u'ID248 Rentrée'] + timedelta(hours=1))
#    print "condition temps", sum(cond_temps)

    cond_hopital = aphp['SITE'] == row['hopital']
#    print "condition hopital et temps", sum((cond_hopital) & (cond_temps))

    cond_age = abs(aphp['age'] - row['age']) < 6
#    print "condition age", sum(cond_age)

    # TODO: ajouter une condition sur la provenance du véhicule
    matchs = aphp[cond_temps & cond_hopital & cond_age]

    # verification
    if len(matchs) > 1:
        cond_origine = matchs['MODE_ARRIVEE'].str.contains(row['CS Affectation'])
        if sum(cond_origine) == 1:
            matchs = matchs[cond_origine]
        else:
            print matchs
            print '\n'
            print row
            import pdb; pdb.set_trace()

    if len(matchs) == 1:
        matched_bspp.loc[idx] = matchs.index.values[0]
        
    if len(matchs) == 0:
        print "condition hopital et temps", sum((cond_hopital) & (cond_temps))
#        import pdb; pdb.set_trace()     

print matched_bspp.notnull().sum()
xxx

list_var_bspp = [u'ID255 Numéro de victime', 'age']
## on travaille par hopital
bspp_APR = bspp.loc[bspp['hopital'] == 'APR', :]
aphp_APR = aphp[aphp['SITE'] == 'APR']

## le premier match c'est quand on a une date de présentation hopital
bspp_APR[u'Engins 538 Présentation Hopital'].convert_objects()


# on cherche sur les caractéristiques des patients/victimes
aphp_APR[['age', u'CODE_POSTAL']]
bspp_APR[[u'Age numérique ', 'ID259 Identification']]
## pour l'instant, on n'a que l'age
bspp_APR.rename(columns={u'Age numérique ':'age'}, inplace=True)

# on coupe par jour
bspp_APR_jour = bspp_APR[bspp_APR[u'ID247 Disponible'] == '01082014']
aphp_APR_jour = aphp_APR[aphp_APR['DATE_ENTREE'].str[:10] == '2014-08-01']


bspp_APR_jour[['age', u'ID247 Disponible']]
aphp_APR_jour[['age', 'DATE_ENTREE']]
# on regarde quand il y a présentation à l'hopital
presentation_pompiers_hopital = bspp_APR[u'Engins 538 Présentation Hopital']


