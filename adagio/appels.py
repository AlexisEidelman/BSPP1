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

appel = read_bspp_table('Appel112_HistoriqueIntervention', nrows = lim_nrows,
                        usecols=[1,2,4])

def PFAU():
    historique = read_bspp_table("Appel112_PFAU_HistoriqueStatutAppel", nrows = 100)
    appel = read_bspp_table("Appel112_PFAU_Appel", nrows = 10000)
    # tables très mal remplies !
    return


tables_to_merge('Appel112_HistoriqueIntervention', exclude=['IdPersonnelPiquet'])




_tables_of_ids(['IdStatutIntervention'])
# L'ordre des identifiants joue, on abandonne le merge pour le faire
# après le changement de format
R_statut = read_bspp_table('Appel112_R_StatutIntervention')
#       IdStatutIntervention AbregeStatutIntervention LibelleStatutIntervention
#    0                     1                      DEB                     Début
#    1                     2                      ENV                     Envoi
#    2                     3                      REC                 Réception
#    3                     4                      VAM       Validation manuelle
#    4                     5                      VAA    Validation automatique
#    5                     6                      ANN                Annulation
#    6                     7                      FIN                       Fin
#    7                     8                      ENC                  En cours
#    8                     9                      RAP         Rapports  rédigés
#    9                    12                      CLA       Cloture automatique
#    10                   13                      CLI      Cloture intervention
#    11                   14                      CLO         Cloture opération
id_cols = ['IdIntervention', 'IdStatutIntervention']
plusieurs_fois_par_intervention = appel[appel.duplicated(id_cols)]['IdIntervention']
appel = appel[~appel['IdIntervention'].isin(plusieurs_fois_par_intervention.unique())]

appel.groupby(id_cols).filter(lambda x: len(x) > 1)

# pas sûr que ce soit robuste avec beaucoup de valeur.
# TODO: garder le caractère puisque l'ordre ne sert pas en définitive
appel['IdStatutIntervention'] = appel['IdStatutIntervention'].astype(int)
appel_format = appel.set_index(id_cols).unstack()
appel_format.columns = [str(x) for x in appel_format]

appel_format = translate_id_into_label('StatutIntervention', appel_format,
    R_statut, method='columns')


print(plusieurs_fois_par_intervention.nunique(), len(appel_format))
# => c'est près de 40% des intervention qu'on a retiré parce que
# plusieurs fois le même statut

appel_format.reset_index(inplace=True) # il faudra retirer ça
appel_format['IdIntervention'] = appel_format['IdIntervention'].astype(str)


def Interventions():
    _tables_of_ids(['IdIntervention'])
#    "Appel112_MMASelection",  Table centrale voir selection.py
#    "Appel112_MMA_AffectationListeDelestage",  vide
#    "Appel112_RessourcePartageeSelection",  non traitée
#    "Appel112_InterventionResume",   agrégat d'autres tables
#    "GestionFlotte_SMSODEIntervention",  lien vers 3300 SMS : pas d'intérêt
#    "Appel112_AdresseIntervention",    voir objets.py
#    "Appel112_SupervisionIntervention", lien vers 10 IP : pas d'intérêt
#    "Appel112_Intervention_FicheDecisionnelle",  valable à partir de 2014-11-06 (voir plus bas)
#    "Appel112_Intervention", 
#    "Appel112_QuestionsOperationnelles",  # voir ci-dessous
#    "Appel112_ArbreDecisionnel_QuestionsIntervention", le ref manque ! dommage
#    "AdagioTools_Historique_cloture_reactivation", 
#    "Appel112_InterventionDelestage", est vide
#    "Appel112_PFAU_Appel", 
#    "Appel112_ArbreDecisionnel_Gestes_Intervention", # traité ci-dessous
#    "Appel112_EvenementIntervention" # est vide
    return
    

def FicheDecisionnelle():
    Fiche = read_bspp_table("Appel112_Intervention_FicheDecisionnelle")
    Fiche = Fiche[['IdIntervention','IdFicheDecisionnelle']]
    R_Fiche = read_bspp_table("Appel112_ArbreDecisionnel_Fiche")
    for nom in ["Categorie", "Pathologie"]:
        nom_table = "Appel112_ArbreDecisionnel_" + nom
        table = read_bspp_table(nom_table)[['Id', 'Libelle']]
        R_Fiche = R_Fiche.merge(table, left_on='Id' + nom,
                            right_on = 'Id', suffixes=('', '_R'))
        del R_Fiche['Id' + nom]
        del R_Fiche['Id_R']
        R_Fiche.rename(columns={'Libelle':nom}, inplace=True)
    
    Fiche = Fiche.merge(R_Fiche, 
                          left_on='IdFicheDecisionnelle',
                          right_on = 'Id',
                          suffixes=('', '_R')
                         )
    return Fiche


def Gestes():
    gestes = read_bspp_table("Appel112_ArbreDecisionnel_Gestes_Intervention")
    R_gestes = read_bspp_table("Appel112_ArbreDecisionnel_Geste")[['Id', 'Libelle']]
    gestes = gestes.merge(R_gestes, left_on='IdGeste',
                          right_on='Id', suffixes=('', '_R')
                          )
    del gestes['IdGeste']
    del gestes['Id_R']
    gestes.rename(columns={'Libelle':'Geste'}, inplace=True)    
    return Gestes


def Questions(lim_nrows=None):
    questions = read_bspp_table("Appel112_QuestionsOperationnelles", nrows=lim_nrows)
    # table de 17 000 000 de lignes
    # Mais R question est vide
    # read_bspp_table("Appel112_ArbreDecisionnel_QuestionsIntervention")




