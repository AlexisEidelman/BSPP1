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
from objets import MMA, Adresses
from variables import tables_to_merge, _tables_of_ids, _ids_of_tables

lim_nrows = 100000

selection = read_bspp_table("Appel112_MMASelection", nrows=lim_nrows,
                            usecols=[0,1,2,4,5,6] # on verra si on ajoute 7
                            #l'observation
                            )
## Les variables
#IdMMASelection                 rend possible le merge avec GestionMMA_HistoriqueMMAStatutOperationnel
#IdIntervention                 rend possible le merge avec Appel112_Intervention et "Appel112_HistoriqueIntervention"
#IdTypeSelection                Traité facilement ci-dessous
#IdInterventionSolution         Ne sert pas, voir ci-dessous, pas dans usecols
#IdMMA                          traité ci-dessous
#IdFamilleRessourcesDotation    traité ci-dessous
#IdAdresseIntervention          traité ci-dessous
#IdTransport                    Ne sert pas je crois. Présent uniquement dans
# RessourcePartagee et je ne sais pas ce que c'est que cette table
#ObservationsPourMMA            object


def correction_selection(tab):
    tab = tab[tab['IdMMA'].notnull()]
    return tab

selection = correction_selection(selection)

def FamilleRessourceDotation():
    # Configuration_FamilleRessourcesDotationStatutOperationnelPossible
    ## => a 6 lignes et peut d'information
    FamRess = read_configuration('FamilleRessourcesDotation')
    # un colonne actif qui vaut 1 tout le temps.
    FamRessType = read_configuration("FamilleRessourcesType")
    FamRess = translate_id_into_label("FamilleRessourcesType", FamRess,
                                      FamRessType)
    return FamRess


def InterventionSolution():
    _tables_of_ids(['IdInterventionSolution'])
    solution = read_bspp_table('Appel112_InterventionSolution', nrows=lim_nrows)
    # cette table est vide
    # => IdInterventionSolution ne sert pas
    # TODO: savoir pourquoi
    return solution


type_selection = read_bspp_table("Appel112_R_TypeSelection").rename(columns={
    'LibeleTypeSelection': 'LibelleTypeSelection'}
    )
selection = translate_id_into_label("TypeSelection",
                                    selection,
                                    type_selection
                                    )

FamilleRessourceDotation = FamilleRessourceDotation()
selection = translate_id_into_label('FamilleRessourcesDotation',
                                    selection, FamilleRessourceDotation,
                                    other_cols=["FamilleRessourcesType"]
                                    )

selection = selection.merge(Adresses(lim_nrows))


if __name__ == '__main__':
    # Libelle_GTA est plus cohérent avec le Cstc de la table adresse
    # que le 'AbregeEgoTools' de la table mma
    
    # il y a un problème entre les cstc de la table adresse 
    mma = MMA()
    selection = selection.merge(MMA())
    
    mma['test_GTA'] = mma.Libelle_GTA.str.split("_").str[2]
    mma.head()
    mma.AbregeEgoTools == mma.test_GTA
    (mma.AbregeEgoTools == mma.test_GTA)
    cond = (mma.AbregeEgoTools == mma.test_GTA)
    cond.value_counts()
    mma[not cond]
    mma[~cond]
    mma[~cond].head()
    mma[~cond].head(20)
    mma[~cond][['Libelle_GTA', 'AbregeEgoTools']]
    adresse = Adresses()
    adresse.head()
    adresse.Cstc.value_counts()
    adresse.Cstc.isin(mma.test_GTA.values)
    sum(adresse.Cstc.isin(mma.test_GTA.values))
    sum(adresse.Cstc.isin(mma.AbregeEgoTools.values))
    len(adresse)
    cond = adresse.Cstc.isin(mma.test_GTA.values)
    adresse[~cond].head()
    adresse[~cond].head(20)
    adresse[~cond]['Cstc'].value_counts(dropna=False)
    99686 - 97976
    "GestionMMA_HistoriqueMoyenSecoursTheoriqueGTA"
    mma[mma.Cstc == 'CCHY']
    mma[mma['Cstc'] == 'CCHY']
    mma.head()
