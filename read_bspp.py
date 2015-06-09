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
#    tab.groupby(['Id_Intervention_Abrege_Motif', 'Code_Cri']).size()
#    gp = tab.groupby(['Id_Statut_Operationnel_Libelle_Statut_Operationnel'])
#    assert all(gp['Abrege_Statut_Operationnel'].nunique() == 1)

    # => on a une redondance, virer l'une des deux
    del tab['Abrege_Statut_Operationnel']

    tab = _rename_bspp_cols(tab)

    date = pd.to_datetime(tab.date, dayfirst=True)
    tab.set_index(date, inplace=True)
    del tab['date']
    return tab


## crée une table avec la définition des intervention
def intervention_table(tab):
    # => 41909 interventions
    id = ['id_intervention']
    def_interevention = ['zone', 'motif_ini', 'motif']
    sub_tab = tab[id + def_interevention]
    sub_tab['date'] = tab.index

    assert max(tab.index.values[:-1] - tab.index.values[1:]) <= 0
    debut = sub_tab.drop_duplicates('id_intervention', take_last=False)
    fin = sub_tab.drop_duplicates('id_intervention', take_last=True)
    intervention = debut.merge(fin, on='id_intervention',
                               suffixes=('', '_fin'))
    intervention.set_index('id_intervention', inplace=True, drop=True)
    return intervention
#    # ancienne version via groupby
#    grouped = intervention.groupby(id)
#    for var in def_interevention:
#        assert all(grouped[var].nunique(dropna=False) == 1)
#    intervention = grouped.first()
#    intervention.drop('date', axis=1, inplace=True)
#    debut = grouped['date'].min()
#    fin = grouped['date'].max()
#
#    for el in ['debut', 'fin']:
#        el_tab = eval(el)
#        el_tab = pd.DataFrame(el_tab)
#        el_tab.columns = [el]
#        intervention = intervention.join(el_tab)


def vehicule_by_intervention(tab):
    # véhicule par intervention
    vehicule = tab.loc[:, ['id_intervention', 'id_vehicule', 'type_ini', 'type']]
    vehicule.drop_duplicates(['id_intervention', 'id_vehicule'], inplace=True)
    vehicule = pd.crosstab(vehicule.id_intervention, vehicule.type)
    return vehicule


def vehicule_table(tab):
    # => 41909 interventions
    id = ['id_vehicule']
    def_vehicule = ['zone_ini']

    vehicule = tab[id + def_vehicule]
    vehicule['date'] = tab.index
    grouped = vehicule.groupby(id)
    for var in def_vehicule:
        assert all(grouped[var].nunique(dropna=False) == 1)
    vehicule = grouped.first()
    vehicule.drop('date', axis=1, inplace=True)
    return vehicule


if __name__ == '__main__':

    tab = read(path)
    ## sujet: brainstorm
    inter = intervention_table(tab)
    # passage possible d'un type de véhicule à un autre
    # tab.groupby(['type','type_ini']).size()
    modif_type = tab.loc[tab.type != tab.type_ini, ['type_ini', 'type']]
    modif_type.drop_duplicates()

    tab['zone_ini_reconstitute'] = tab.id_vehicule.str.split('_').str[2]
    tab.groupby(['zone_ini', 'zone_ini_reconstitute']).size()
    test = tab['zone_ini_reconstitute'] != tab['zone_ini']

    # on regarde si un motif d'intervention a toujours le même véhicule appelé



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