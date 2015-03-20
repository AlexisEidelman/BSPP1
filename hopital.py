# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 17:01:55 2015

@author: Alexis Eidelman
"""

import pandas as pd
import os

import

path = 'D:\data\BSPP'
main_file = os.path.join(path, '2015-043-Extraction LCL PAGNIEZ.csv')

tab = pd.read_csv(main_file, sep=',', encoding='utf8')

## quelques stats
tab['Id_Intervention'].value_counts()
tab[u'Id_Statut_Operationnel_Libelle_Statut_Operationnel'].value_counts()

# recherche de variables redondantes
tab.groupby(['Id_Intervention_Abrege_Motif', 'Code_Cri']).size()
gp = tab.groupby(['Id_Statut_Operationnel_Libelle_Statut_Operationnel'])
assert all(gp['Abrege_Statut_Operationnel'].nunique() == 1)
# => on a une redondance, virer l'une des deux
del tab['Abrege_Statut_Operationnel']



def rename_bspp_cols(tab):
    tab.columns = ['date', 'id_intervention', 'motif_ini', 'motif',
                   'zone', 'zone_ini',
                   'id_vehicule', 'type_ini', 'type', 'statut']



## sujet: brainstorm


# étudier les différences entre 'Id_Intervention_Abrege_Motif' et 'cri'
# ce qui est établi et ce qui est constaté
# => Demander à la BSPP si c'est grave de se tromper d'intervention, faire baisser ce taux en
# regardant dans quels cas il se produit
tab.groupby(['Id_Intervention_Abrege_Motif', 'Code_Cri']).size()

## expliquer l'indisponibilité des véhicules
# quel heure ont lieu les manques de personnels !
tab[u'Id_Statut_Operationnel_Libelle_Statut_Operationnel'].value_counts()

## guide des intéractions avec l'hopital
hopital = [u'Transport hôpital', u"Arrivée hôpital", u"Quitte hôpital"]
tab_hopital = tab[tab[u'Id_Statut_Operationnel_Libelle_Statut_Operationnel'].isin(hopital)]
assert len(tab_hopital) == 33302  #
tab_hopital['Id_Intervention'].value_counts()
# un exemple : il y a plusieurs véhicules par intérventions
# -> on peut suivre le véhicule et voir combien de temps il reste à l'hopital
# une stat à améliorer ou bien il faut laisser les pomiers draguer les infirmières ?
tab_hopital[tab_hopital['Id_Intervention'] == 8420079]