# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 13:51:08 2015

@author: Alexis Eidelman
"""

import pandas as pd
import os

path = 'D:\data\BSPP'

list_tables = ['Intervention', 'Victimes', 'Statuts Engins', 'Engin']

def read(table, path=path):
    main_file = os.path.join(path, 'Export civil - ' + table + ' (1au4-08-2014).csv')
    tab = pd.read_csv(main_file, sep=';', encoding='cp1252')
    return tab


for table in list_tables:
    read(table)