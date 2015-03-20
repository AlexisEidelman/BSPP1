# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 17:27:32 2015

@author: Alexis Eidelman
"""

import pandas as pd
import os

path = 'D:\data\BSPP'



def _rename_bspp_cols(tab):
    tab.columns = ['date', 'id_intervention', 'motif_ini', 'motif',
                   'zone', 'zone_ini',
                   'id_vehicule', 'type_ini', 'type', 'statut']
    return tab


def read(path=path):
    main_file = os.path.join(path, '2015-043-Extraction LCL PAGNIEZ.csv')
    tab = pd.read_csv(main_file, sep=',', encoding='utf8')

    ## quelques stats
    tab['Id_Intervention'].value_counts()
    tab[u'Id_Statut_Operationnel_Libelle_Statut_Operationnel'].value_counts()

    # recherche de variables redondantes
    tab.groupby(['Id_Intervention_Abrege_Motif', 'Code_Cri']).size()
    gp = tab.groupby(['Id_Statut_Operationnel_Libelle_Statut_Operationnel'])
#    assert all(gp['Abrege_Statut_Operationnel'].nunique() == 1)

    # => on a une redondance, virer l'une des deux
    del tab['Abrege_Statut_Operationnel']

    tab = _rename_bspp_cols(tab)

    date = pd.to_datetime(tab.date, dayfirst=True)
    tab.set_index(date, inplace=True)
    del tab['date']
    return tab


if __name__ == '__main__':

    tab = read(path)
    ## sujet: brainstorm

    # étudier les différences entre 'Id_Intervention_Abrege_Motif' et 'cri'
    # ce qui est établi et ce qui est constaté
    # => Demander à la BSPP si c'est grave de se tromper d'intervention, faire baisser ce taux en
    # regardant dans quels cas il se produit
    tab.groupby(['motif_ini', 'motif']).size()

    ## expliquer l'indisponibilité des véhicules
    # quel heure ont lieu les manques de personnels !
    tab['statut'].value_counts()

    ## guide des intéractions avec l'hopital
    hopital = [u'Transport hôpital', u"Arrivée hôpital", u"Quitte hôpital"]
    tab_hopital = tab[tab['statut'].isin(hopital)]
    assert len(tab_hopital) == 33302  #
    tab_hopital['id_intervention'].value_counts()
    # un exemple : il y a plusieurs véhicules par intérventions
    # -> on peut suivre le véhicule et voir combien de temps il reste à l'hopital
    # une stat à améliorer ou bien il faut laisser les pomiers draguer les infirmières ?
    tab_hopital[tab_hopital['id_intervention'] == 8420079]


    ## regarder les déplacements hors zone...

    # TODO: changer le nom des variables à rallonge