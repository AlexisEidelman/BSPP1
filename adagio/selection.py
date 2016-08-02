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


selection = read_bspp_table("Appel112_MMASelection", nrows=100000)

def correction_selection(tab):
    tab = tab[tab['IdMMA'].notnull()]
    return tab

selection = correction_selection(selection)
## Les variables
#IdMMASelection                 Inutile
#IdIntervention                 object
#IdTypeSelection                object
#IdInterventionSolution         object
#IdMMA                          object
#IdFamilleRessourcesDotation    object
#IdAdresseIntervention          object
#IdTransport                    Ne sert pas je crois. Présent uniquement dans 
# RessourcePartagee et je ne sais pas ce que c'est que cette table
#ObservationsPourMMA            object


