# -*- coding: utf-8 -*-
"""
La table la plus centrale est la base séléction.
C'est elle qui est le point de départ de ce programme et qu'on enrichit

@author: alexis
"""

import datetime
import pandas as pd

from read import read_bspp_table, read_configuration
from tools import translate_id_into_label
from variables import tables_to_merge, _tables_of_ids, _ids_of_tables

lim_nrows = 100000

selection = read_bspp_table("Appel112_MMASelection", nrows=lim_nrows,
                            usecols=[1,2,3,4,5,6] # on verra si on ajoute 7
                            #l'observation
                            )

def correction_selection(tab):
    tab = tab[tab['IdMMA'].notnull()]
    return tab

selection = correction_selection(selection)
## Les variables
#IdMMASelection                 merge avec les interventions usecols
#IdIntervention                 object
#IdTypeSelection                object
#IdInterventionSolution         object
#IdMMA                          traité ci-dessous
#IdFamilleRessourcesDotation    traité ci-dessous
#IdAdresseIntervention          traité ci-dessous
#IdTransport                    Ne sert pas je crois. Présent uniquement dans
# RessourcePartagee et je ne sais pas ce que c'est que cette table
#ObservationsPourMMA            object

def FamilleRessourceDotation():
    # Configuration_FamilleRessourcesDotationStatutOperationnelPossible
    ## => a 6 lignes et peut d'information
    FamRess = read_configuration('FamilleRessourcesDotation')
    # un colonne actif qui vaut 1 tout le temps.
    FamRessType = read_configuration("FamilleRessourcesType")
    FamRess = translate_id_into_label("FamilleRessourcesType", FamRess,
                                      FamRessType)
    return FamRess


def Adresses():
    # Cette fonction reperend ce qui est fait dans le fichier appels.py
    # TODO: faire une seule fonction partagée
    adresse = read_bspp_table("Appel112_AdresseIntervention", nrows=lim_nrows)
    adresse.drop_duplicates(inplace=True)

    # les identifiants IdObjetGeO et IdAdresse qui sont confondu dans la table
    # résumé intervention ont un intérêt pour l'instant peu évident.

    # le type des adresses
    TypeAdresse = read_bspp_table('Appel112_R_TypeAdresse')
    adresse = translate_id_into_label('TypeAdresse', adresse, TypeAdresse)
    del TypeAdresse

    return adresse



def MMA():
    '''
    #####  les infos sur le MMA ######
    # Cette fonction reperend ce qui est fait dans le fichier duree_intervention.py
    # TODO: faire une seule fonction partagée '''
    mma = read_configuration('MMA')
    # on utilise pas l'originel (mais on pourrait)
    del mma['IdFamilleMMAOriginelle']
    #TODO savoir ce qu'est un Omnibus
    to_remove = ['ImmatriculationBSPPMMA', 'ImmatriculationAdministrativeMMA',
                 'RFGI', 'GSM', 'Actif', 'Strada', 'Omnibus',
                 'Associe', 'OrdreGTA', 'Disponible', 'Observation',
                 'IdStatutOperationnel']
    mma.drop(to_remove, axis=1, inplace=True)

    # famille mma
    famille_mma = read_configuration('FamilleMMA')
    del famille_mma['FamilleMMA'] # qui est vide
    mma.rename(columns={'IdFamilleMMAOperationnelle': 'IdFamilleMMA'}, inplace=True)
    var_nombre = [var for var in famille_mma.columns if 'Nombre' in var]
    mma = translate_id_into_label('FamilleMMA', mma, famille_mma,
        other_cols = var_nombre)

    # Apparentance
    appartenance = read_configuration('MoyenSecoursAppartenance')
    mma = translate_id_into_label('MoyenSecoursAppartenance', mma, appartenance)

    #IdFamilleMMAModele
    assert all(mma.IdFamilleMMAModele == '1')
    # donc variable ininteressante
    # donc MMAModele = read_configuration('FamilleMMAModele') ne sert � rien
    # donc:
    del mma['IdFamilleMMAModele']

    # IdLieuStationnementOperationnel
    # et
    # IdAffectationAdministrative
    def caserne():
        ''' on peut se servir de cette table pour
            remonter sur chaque casernes, l'info de la compagnie
            a laquelle elle appartient et ainsi de suite
        '''
        base = read_bspp_table("AdagioTools_ArborescenceEGOTools")
        assert(all(base.IdTypeEgoTools == '1')) # on pourrait fusionner avec
        # "AdagioTools_R_TypeEGOTools" et on aurait le label  "Brigade de
        # Sapeurs-Pompiers de Paris"
        # IdAgoTools permet de relier à d'autres tables comme "affectation administrative"
        del base['IdTypeEgoTools']

        TypeArboresences = read_bspp_table("AdagioTools_R_TypeArborescenceEGOTools")
        base = translate_id_into_label('TypeArborescenceEgoTools',
                                           base, TypeArboresences)

        casernes = base[base['TypeArborescenceEgoTools'] == 'Lieu de stationnement opérationnel']
        compagnies = base[base['TypeArborescenceEgoTools'] == "Compagnie d'Incendie et de Secours"]
        groupements = base[base['TypeArborescenceEgoTools'] == "Groupement d'Incendie et de Secours"]
        # chaque base dans une compagnie ?
        all(casernes['IdArboEgoToolsPERE'].isin(compagnies['IdArboEgoTools']))
        all(compagnies['IdArboEgoToolsPERE'].isin(groupements['IdArboEgoTools']))
        compagnies = compagnies.merge(groupements[['IdArboEgoTools', 'LibelleEgoTools']],
                                      left_on='IdArboEgoToolsPERE',
                                      right_on='IdArboEgoTools',
                                      suffixes=('', '_gpt'))

        casernes = casernes.merge(compagnies[['IdArboEgoTools', 'LibelleEgoTools', 'LibelleEgoTools_gpt']],
                                      left_on='IdArboEgoToolsPERE',
                                      right_on='IdArboEgoTools',
                                      suffixes=('', '_cie'))

        casernes.rename(columns={'LibelleEgoTools_gpt': 'Groupement',
                             'LibelleEgoTools_cie': 'Compagnie'},
                             inplace=True)

        casernes = casernes[['IdEgoTools','LibelleEgoTools',
                             'Groupement', 'Compagnie']]
        return casernes

    casernes = caserne()
    mma = mma.merge(casernes, left_on='IdLieuStationnementOperationnel',
                  right_on= 'IdEgoTools', how='left')
    del mma['IdEgoTools']
    return mma



FamilleRessourceDotation = FamilleRessourceDotation()
selection = translate_id_into_label('FamilleRessourcesDotation',
                                    selection, FamilleRessourceDotation,
                                    other_cols=["FamilleRessourcesType"]
                                    )

selection = selection.merge(Adresses())

selection = selection.merge(MMA())


