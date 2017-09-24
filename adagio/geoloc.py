# -*- coding: utf-8 -*-

import datetime
import pandas as pd

from read import read_bspp_table, read_configuration
from tools import translate_id_into_label

tab1 = read_bspp_table("GestionFlotte_HistoriqueLocalisationMMA",
                      nrows=10,
                      usecols=[1,2,3,4,5])

tab2 = read_bspp_table("GestionFlotte_LienLocalisationMMAStatutOperationnel",
                      nrows=10)


RFGI_IdMMA = read_bspp_table("GestionFlotte_HistoriqueLocalisationMMA",
                      usecols=[1,5])