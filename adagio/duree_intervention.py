# -*- coding: utf-8 -*-
"""
@author: aeidemlan
"""

from adagio import read_bspp_table

tab = read_bspp_table('Appel112_HistoriqueIntervention',
                      nrows=10000)

# est-ce qu'on peut passer du GMT ?
heure = tab['GroupeHoraireModificationStatut'].str[11:13]
heureGMT = tab['GroupeHoraireModificationStatutGMT'].str[11:13]
diff = heure.astype(int) - heureGMT.astype(int)
diff.value_counts()
# => on doit avoir les changements d'heure d'hiver
assert all(tab.IdHistoriqueIntervention.value_counts() == 1)

# tab.IdStatutIntervention prend 9 valeurs

tab = read_bspp_table('Appel112_HistoriqueAppel', nrows=10000)
# on a l'heure de début et l'heure de fin

tab = read_bspp_table('AdagioTools_Historique_Test', nrows = 100)
# pas de date

tab = read_bspp_table('Appel112_InterventionResume', nrows = 100)
tab = read_bspp_table('Appel112_Intervention', nrows = 10000)
tab = read_bspp_table('Appel112_HistoriqueIntervention', nrows = 10000)
tab = read_bspp_table('Appel112_CTI', nrows = 10000)

tab = read_bspp_table('GestionFlotte_HistoriqueLocalisationMMA', nrows = 10000)
tab = read_bspp_table("GestionMMA_HistoriqueMMAStatutOperationnel")
# 2133067 lignes


tab = read_bspp_table("GestionMMA_HistoriqueMMAStatutOperationnel", nrows = 10000)

# probleme avec les tables évenment ?
tab = read_bspp_table("Appel112_Evenement", nrows = 10000)
tab_engin = read_bspp_table("Configuration_R_MMA")
tab = read_bspp_table("gdh_Etablissements", nrows = 10000)
