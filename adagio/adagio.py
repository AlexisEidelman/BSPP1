# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 12:20:50 2016

@author: aeidelman
"""

import os
import io
import pandas as pd

from read_sql_tables import parsed_sql

path_data = '/home/sgmap/data/BSPP/tables1'

groupes = ['AdagioTools','Appel112','Bipi',
          'communication','Configuration','gdh',
          'Geographie','GestionFlotte','GestionMMA',
          'Gouverneur','MRSA','Rapport',
          'sécurité_ADAGIO','Sigtao,SonnerieDeFeux']

def read_bspp_table(name, nrows=None):
    separator = '\\\t'    
    path = os.path.join(path_data, name + '.txt')

    tab = pd.read_csv(path , sep=separator, nrows=nrows,
                       header=None, encoding='cp1252'
                       )
#    except:
#        tab = pd.read_csv(path , sep=separator, nrows=nrows,
#                           header=None, encoding='cp1252',
#                           error_bad_lines=False)
#        with io.open(path, encoding='cp1252') as infile:
#            for line in infile[:nrows]:
#        import pdb
#        print(name)
#        pdb.set_trace()
#
#        print("pour la table ", name, " demander pour quoi il y a ",
#            " des erreurs")
    for col in tab.columns:
        if tab[col].dtype == 'object':
            tab[col] = tab[col].str.replace('\t', '')
            tab[col] = tab[col].str.replace('\\', '')
            
    if all(tab.iloc[:,-1].isnull()):
        tab = tab.iloc[:,:-1]
    assert len(tab.columns) == len(parsed_sql[name])
    tab.columns = parsed_sql[name]        
    return tab


if __name__ == '__main__':
    # localisation 
#    localisation = read_bspp_table('GestionFlotte_LienLocalisationMMAStatutOperationnel')
#    statut_op = read_bspp_table('GestionMMA_HistoriqueMMAStatutOperationnel')
#    omnibus = read_bspp_table('GestionMMA_HistoriqueOmnibus')
#    
    len(os.listdir(path_data))
    for table in parsed_sql.keys():
        groupe = [x for x in groupes if table.startswith(x)]
        print(groupe)
        if groupe == []:
            print('..........pb with ....', table)

    reperage_identifiant = dict()
    for name, variables in parsed_sql.items():
        for var in variables:
            if var.startswith('Id'):
                if var in reperage_identifiant:
                    reperage_identifiant[var].append(name)
                else:
                    reperage_identifiant[var] = [name]
    import json
    with open('identifiant.json', 'w') as outfile:
        json.dump(reperage_identifiant, outfile, sort_keys = True, indent = 4,
                  ensure_ascii=False)
    