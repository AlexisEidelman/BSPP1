# -*- coding: utf-8 -*-
"""

Travaille sur la base Appel

Note: le travail sur la base PFAU est-peut-être encore plus intéressant
# TODO: a regarder


@author: aeidelman
"""

import datetime
import pandas as pd

from read import read_bspp_table, read_configuration
from variables import tables_to_merge, _tables_of_ids, _ids_of_tables
from tools import translate_id_into_label

lim_nrows = 10000

appel = read_bspp_table('Appel112_HistoriqueIntervention', nrows = 100000,
                        usecols=[1,2,4])

tables_to_merge('Appel112_HistoriqueIntervention', exclude=['IdPersonnelPiquet'])

_tables_of_ids(['IdStatutIntervention'])
_tables_of_ids(['IdIntervention'])

# L'ordre des identifiants joue, on abandonne le merge pour le faire
# après le changement de format
R_statut = read_bspp_table('Appel112_R_StatutIntervention')
for col in R_statut.columns:
    if col.startswith('Abrege'):
        if col.replace('Abrege', 'Libelle') in R_statut.columns:
            del R_statut[col]

#assert appel['IdStatutIntervention'].isnull().sum() == 0
#appel = appel.merge(R_statut)
#del appel['IdStatutIntervention']


id_cols = ['IdIntervention', 'IdStatutIntervention']
plusieurs_fois_par_intervention = appel[appel.duplicated(id_cols)]['IdIntervention']
appel = appel[~appel['IdIntervention'].isin(plusieurs_fois_par_intervention.unique())]


appel.groupby(id_cols).filter(lambda x: len(x) > 1)

# pas sûr que ce soit robuste avec beaucoup de valeur.
# TODO: garder le caractère puisque l'ordre ne sert pas en définitive
appel['IdIntervention'] = appel['IdIntervention'].astype(int)
appel_format = appel.set_index(id_cols).unstack()
appel_format.columns = appel_format.columns.levels[1]

appel_format = translate_id_into_label('StatutIntervention', appel_format, R_statut)


print(plusieurs_fois_par_intervention.nunique(), len(appel_format))
# => c'est près de 40% des intervention qu'on a retiré parce que 
# plusieurs fois le même statut

appel_format.reset_index(inplace=True) # il faudra retirer ça
appel_format['IdIntervention'] = appel_format['IdIntervention'].astype(str)






###  La table adresse 
adresse = read_bspp_table('Appel112_AdresseIntervention', nrows=100000)

_tables_of_ids(['IdAdresseIntervention']) # c'est l'index de la base, 
all(adresse.IdAdresseIntervention.value_counts() == 1)
# => pas d'intérêt 
del adresse['IdAdresseIntervention']

adresse.drop_duplicates(inplace=True)

# les identifiants adresses (qui est en fait 'IdObjetGeo')
_tables_of_ids(['IdObjetGeo'])
# pas d'intérêt

# le type des adresses
_tables_of_ids(['IdTypeAdresse'])
TypeAdresse = read_bspp_table('Appel112_R_TypeAdresse')
adresse = translate_id_into_label('TypeAdresse', adresse, TypeAdresse, method='merge')
del TypeAdresse

_tables_of_ids(['IdObjetGeo']) 
# => aucun intérêt



# parcelle est vide ! 
parcelle = read_bspp_table('Appel112_ParcellaireIntervention')
_tables_of_ids(_ids_of_tables(['Appel112_ParcellaireIntervention']))


resume = read_bspp_table('Appel112_InterventionResume', nrows=100000)
tables_to_merge('Appel112_InterventionResume',
                exclude=['IdPersonnelPiquet','IdIntervention'])
#  beaucoup de variables sont dans la table adresse.
# IdObjetGeo est IdAdresse dans la table AdresseIntervention alors qu'elle 
# contient aussi un IdObjetGeo différent
# les coordonnées X, Y changent de nom et sont arrondies.

# le lien entre IdIntervention et 'IdGrilleDepart est la vraie richesse
# de la base resume
# surtout qu'on n'a pas le table InterventinoSolution (elle est vide)
motif = read_configuration('MotifAlerte')
_tables_of_ids(['IdMotifAlertePreavis'])
_tables_of_ids(['IdIntervention'])