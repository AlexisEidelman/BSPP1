# -*- coding: utf-8 -*-
"""

@author: aeidelman
"""

import os
import json

from config import config
from colnames_by_table import colnames_by_table

path_data = config['PATH']['DATA']
path_dico = config['PATH']['DICTIONNAIRE']

groupes = ['AdagioTools','Appel112','Bipi',
          'communication','Configuration','gdh',
          'Geographie','GestionFlotte','GestionMMA',
          'Gouverneur','MRSA','Rapport',
          'sécurité_ADAGIO','Sigtao,SonnerieDeFeux']


## verifie que toutes les tables sont dans un groupe
len(os.listdir(path_data))
for table in colnames_by_table.keys():
    groupe = [x for x in groupes if table.encode('utf8').startswith(x)]
    print(groupe)
    if groupe == []:
        print('..........pb with ....', table)


## créer les liens entre variables et surtout pour les identifiants
tables_by_names = dict()
reperage_all_but_id = dict()
for name, variables in colnames_by_table.items():
    for var in variables:
        if var in tables_by_names:
            tables_by_names[var].append(name)
        else:
            tables_by_names[var] = [name]

tables_by_id = dict((key, value)
    for key, value in tables_by_names.items()
    if key.startswith('Id')
    )

tables_by_id_to_merge =  dict((key, value)
    for key, value in tables_by_id.items()
    if len(value) > 1
    )


##enregistrer les fichier ci-dessus
def save_tables_by_id():
    with open('tables_by_var.json', 'w') as outfile:
        json.dump(tables_by_names, outfile, sort_keys = True, indent = 4,
                  ensure_ascii=False)

    with open('identifiants.json', 'w') as outfile:
        json.dump(tables_by_id_to_merge, outfile, sort_keys = True, indent = 4,
              ensure_ascii=False)


# trouver toutes les bases avec les identifiants
def _ids_of_tables(tables, exclude=None):
    ''' 
    trouve tous identifiants des tables
    '''
    assert isinstance(tables, list)
    assert len(tables) == len(set(tables)) # pas de doublons        
    ids = []
    for table in tables:
        colnames = colnames_by_table[table]
        if exclude is not None:
            colnames = [x for x in colnames if x not in exclude]
        colnames = [x for x in colnames 
            if x.startswith('Id') and x not in ids]
        ids += colnames
    return ids
    

def _tables_of_ids(ids):
    ''' 
    trouve les tables contenant les ids
    '''
    assert isinstance(ids, list)
    assert len(ids) == len(set(ids)) # pas de doublons        
    tables = []
    for ident in ids:
        if ident in tables_by_id_to_merge:
            to_add = [x for x in tables_by_id_to_merge[ident] if x not in tables]
            tables += to_add
    return tables


def tables_to_merge(table_name, exclude=None):
    ''' trouve tou les bases connectée à une table
        via les identifiants '''
    # il faut faire attention à éviter les boucles
    table_to_merge_with = [table_name]
    idents_before = []
    idents_after = _ids_of_tables(table_to_merge_with, exclude)
    count = 0
    while idents_after != idents_before:
        idents_before = idents_after
        table_to_merge_with = _tables_of_ids(idents_before)
        idents_after = _ids_of_tables(table_to_merge_with, exclude)
        print(count)
        count += 1
    
    return table_to_merge_with


if __name__ == '__main__':
    save_tables_by_id()


