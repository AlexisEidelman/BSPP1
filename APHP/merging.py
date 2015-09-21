# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 13:59:25 2015

@author: Alexis Eidelman
"""

import pandas as pd

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


###### MATCHING PROPREMENT DIT #####
list_var_bspp = [u'ID255 Numéro de victime', 'age',
                 ]
## on travaille par hopital
bspp_APR = bspp.loc[bspp['hopital'] == 'APR', [u'ID202 Numéro Intervention',]]
aphp_APR = aphp[aphp['SITE'] == 'APR']

## le premier match c'est quand on a une date de présentation hopital
bspp_APR[u'Engins 538 Présentation Hopital']


# on cherche sur les caractéristiques des patients/victimes
aphp_APR[['age', u'CODE_POSTAL']]
bspp_APR[[u'Age numérique ', 'ID259 Identification']]
## pour l'instant, on n'a que l'age
bspp_APR.rename(columns={u'Age numérique ':'age'}, inplace=True)

# on coupe par jour
bspp_APR_jour = bspp_APR[bspp_APR[u'ID247 Disponible'].str[:10] == '01/08/2014']
aphp_APR_jour = aphp_APR[aphp_APR['DATE_ENTREE'].str[:10] == '2014-08-01']


bspp_APR_jour[['age', u'ID247 Disponible']]
aphp_APR_jour[['age', 'DATE_ENTREE']]
# on regarde quand il y a présentation à l'hopital
presentation_pompiers_hopital = bspp_APR[u'Engins 538 Présentation Hopital']


