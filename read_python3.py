"""
Created on Thu Mar 19 17:27:32 2015
@author: Florian Gauthier
"""

import os
import numpy as np
import pandas as pd

from collections import Counter

from read import read
from read import _rename_bspp_cols
from tools_bspp import zeros_rm

path = 'D:\data\BSPP'

tab = read(path)
tab.columns
tab.index

# Quels sont les motifs avec lesquels on se trompe le plus ?

    ######################
    #   Data Cleaning    #
    ######################

tab[u'motif_ini'].value_counts()
z = tab[u'motif_ini'] == tab[u'motif']
Counter(z)

tab.dtypes

#On convertit toutes les variables en "object"
tab.motif = tab.motif.astype(object)
tab.id_intervention = tab.id_intervention.astype(object)

# On enlève les ".0"
tab["motif"] = tab["motif"].apply(zeros_rm)
tab["motif_ini"] = tab["motif_ini"].apply(zeros_rm) #value error


    ######################
    #    Stats descr     #
    ######################



tab.head()

    ########################################
    #    Durées moyenne / intervention     #
    ########################################
# Objectif : calculer la durée d'intervention moyenne par motif

tab['id_intervention'].value_counts()
tab['date'] = tab.index #on récup la date pour simplifier les calculs

group = tab.groupby('id_intervention') 
# TODO : pourquoi ça change quand on groupby motif ? (ah j'ai compris : motif se répètent dans les interventions)
t_duree = group.agg({'date' : [np.min, np.max]})
t_duree = t_duree.reset_index()
t_duree['duree'] = t_duree['date']['amax'] - t_duree['date']['amin']
t_duree = t_duree.iloc[:,[0,3]]
#on se débarasse des index de t_duree
t_duree = t_duree.reset_index()
del t_duree['index']
t_duree.columns = ['id_intervention','duree']
(t_duree['duree'] / np.timedelta64(1,'m')).plot(legend=True)

t_duree['duree'].value_counts()
# 223 interventions à durée nulle.

 ### jusqu'ici tout est OK niveau durée.

#Table : intervention <-> motif 
gp_id = tab.groupby(['id_intervention','motif']).first().reset_index()
t_id_motif = gp_id.iloc[:,0:2]
t_id_motif['motif'].value_counts()
t_duree = t_duree.merge(t_id_motif,on='id_intervention', how='outer')

#  motif & nb de motifs
gp_counts = t_duree['motif'].value_counts()
gp_counts = pd.DataFrame(gp_counts.reset_index())
gp_counts.columns = ["motif","count"]

#  motifs & somme des durées des motifs
gp_sum = t_duree.groupby(['motif'])["duree"].sum().reset_index()
gp_sum.columns = ["motif","sum_duree"]

#  Table : Durée moyenne par motif
motif_duration = gp_sum.merge(gp_counts, on='motif', how='outer')
motif_duration["moy_duree"] = motif_duration["sum_duree"] / motif_duration["count"]
#motif_duration["moy_duree"] / np.timedelta64(1,'m')
motif_duration.sort(['moy_duree'], ascending = False)

                ##########################################
                #    Stats : durées des interventions    #
                ##########################################
# Trucs marrants 
#Personne blessée (lieu privé) (352) => Interventions les plus longues ! (moy = 1 jour et 8h)
            # certaines interventions tirent la moyenne vers le haut (plusieurs jours)
            # par ex, l'intervention "8325876" qui dure 9 jours !!
#Fuite de climatisation & Fuite de gaz (614 & 610) ont tendance à prendre du temps (env 4h)
#Exercice "maison du feu" (971) dure environ une journée et demi 

# Objectif : Perte de temps -> Faire la différence entre la durée du motif_ini et du motif réel

t_motif_duree = motif_duration.iloc[:,[0,3]]
t_motif_duree.columns = ['motif','moy_duree_motif']
#  table pour merger avec les bons labels
t_motif_ini_duree = t_motif_duree
t_motif_ini_duree.columns = ['motif_ini','moy_duree_motif_ini']

#Nombre de motif_ini
nb_motif_ini = tab.groupby(["motif_ini"]).size().reset_index()
nb_motif_ini.columns = ['motif_ini', 'nb_ini']
nb_motif_ini.sort(['nb_ini'], ascending=False)

# Les index pour lesquels il y a une erreur
erreurs = tab.motif_ini != tab.motif
tab['erreur'] = erreurs
t_count_error = tab.groupby(["motif_ini","motif"])['erreur'].sum()
t_count_error.sort(ascending=False)
t_count_error = t_count_error.reset_index()
t_count_error.columns = ['motif_ini', 'motif', 'nb_erreurs']
t_count_error = t_count_error.merge(nb_motif_ini, on='motif_ini')
t_count_error['err_percentage'] = t_count_error['nb_erreurs'] / t_count_error['nb_ini']

t = t_count_error.merge(t_motif_duree, on='motif', how = 'outer')
t = t.merge(t_motif_ini_duree, on='motif_ini', how='outer')
t.head()
t['diff'] = t['moy_duree_motif_ini'] - t['moy_duree_motif']
t_diff_final = t.iloc[:,[0,1,2,4,7]]
## on enlève les valeurs nulles
t_diff_final = t_diff_final[t_diff_final['diff'].isnull() != True]
t_diff_final.sort(['err_percentage'], ascending = False)

                ###################
                #    Résultats    #
                ###################
#### Les interventions qui prennent + de temps que ce qui est prévu (en moy) ####
## % : nb_erreurs/nb(motif_ini)

#  603 (assèchement des locaux) -> 610 (fuite de gaz)  => 3H30 de plus   100%
#  335(personne coincée dans un ascenceur) -> 332 (personne tombée)    100%
# 910 (engin explosif) -> 934 (???)   40 min de plus   100%
# 713 (matériaux menaçant de chuter) -> 730 (protection aire de poser helicoptère) 40min de plus   78%
#  721 (chaudière)  -> 711 (???)  -> 2h de plus    55%
#  601 (innondation importante)  -> 610 (Fuite de gaz, butane, propane)   2H40 de plus   49%

# TODO : Regarder les commentaire "Manque de personnel" !!! => Les heures auxquelles ça arrive
# le code correspondant "Abrege_Statut_Operationnel" est "IMPER" 
# Il n'y en a que 27 : regarder direct dans excel. Difficile d'aller plus loin.



# Objectif : 