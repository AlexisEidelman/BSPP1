# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 17:01:55 2015

@author: Alexis Eidelman
"""

import numpy as np

from read import read


tab = read()

## guide des intéractions avec l'hopital
hopital = [u'Transport hôpital', u"Arrivée hôpital", u"Quitte hôpital"]
tab_hopital = tab[tab['statut'].isin(hopital)]
gp = tab_hopital.groupby(['id_intervention', 'id_vehicule'])

def etudie_groupe(gp, taille_du_groupe):
    gp1 = gp.filter(lambda g: len(g) == taille_du_groupe)
    #    gp1['statut'].value_counts()
    #    gp1['indic'] = 1
    #    gp1['test'] = gp1['indic'].cumsum()
    gp1 = gp1[['id_intervention', 'zone', 'id_vehicule', 'type', 'statut']]
    return gp1

gp1 = etudie_groupe(gp, 1)
# => pas de date privilégiée...

gp2 = etudie_groupe(gp, 2)
gp3 = etudie_groupe(gp, 3)


def _un_de_chaque(group):
    return group['statut'].nunique() == 3

# on ne garde que les cas avec échange à l'hopital
select_gp3 = gp3.groupby(['id_intervention', 'id_vehicule']).filter(_un_de_chaque)
# TODO: définir, la valeur


def diff_arrivee_quitte(group):
    arrivee = group[group['statut'] == u"Arrivée hôpital"].index[0]
    depart = group[group['statut'] == u"Quitte hôpital"].index[0]
    return depart - arrivee

### test

voir = select_gp3.groupby(['id_intervention', 'id_vehicule']).get_group((8288106, 'VSAV BSPP_1_STCL'))

test = select_gp3.groupby(['id_intervention', 'id_vehicule']).apply(diff_arrivee_quitte)
(test / np.timedelta64(1,'m')).hist()


# regarder maintenant par zone, par type de véhicule par moment de la journée.

assert len(tab_hopital) == 33302  #
tab_hopital['id_intervention'].value_counts()
# un exemple : il y a plusieurs véhicules par intérventions
# -> on peut suivre le véhicule et voir combien de temps il reste à l'hopital
# une stat à améliorer ou bien il faut laisser les pomiers draguer les infirmières ?
test = tab_hopital[tab_hopital['id_intervention'] == 8420079]