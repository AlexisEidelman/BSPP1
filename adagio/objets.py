# -*- coding: utf-8 -*-
"""
Ce programme récupère des objets important des tables BSPP.
    - les adresses
    - les caserners
    - les vehicules

Il se veut être le plus complet sur chacun d'entre eux

@author: aeidelman

"""

from read import read_bspp_table, read_configuration
from tools import translate_id_into_label

def Adresses(lim_nrows=None):
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

    # parcelle est vide !
    #parcelle = read_bspp_table('Appel112_ParcellaireIntervention')

    return adresse


def Caserne():
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

    casernes = casernes[['IdEgoTools','LibelleEgoTools', 'AbregeEgoTools',
                         'Groupement', 'Compagnie']]
    return casernes


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
    #TODO: 
    # On pourrait regarder RFGI avec GestionFlotte_R_RFGI
    # 
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


    casernes = Caserne()
    mma = mma.merge(casernes, left_on='IdLieuStationnementOperationnel',
                  right_on= 'IdEgoTools', how='left')
    del mma['IdEgoTools']
    return mma
