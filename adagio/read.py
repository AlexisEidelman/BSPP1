# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22

Une fonction pour lire une table en lui ajoutant
des headers.

Une autre pour lire les fichiers de configurations


@author: aeidelman
"""

import os
import io
import pandas as pd

from config import config
from colnames_by_table import colnames_by_table

path_data = config['PATH']['DATA']

def read_bspp_table(name, nrows=None, skiprows=None,
                    usecols=None,
                    optim = False):
    separator = '\\\t'
    path = os.path.join(path_data, name + '.txt')

    if name + '.txt' in os.listdir(os.path.join(path_data, 'empty_files')):
        raise Exception('Le fichier ' + name + ' est vide')

    if optim:
        pass
    else:
        tab = pd.read_csv(path , sep=separator,
                      nrows=nrows, skiprows=skiprows,
                       header=None, encoding='cp1252',
                       usecols=usecols,
                       # TODO: tester cette option pour avoir un meilleur
                       # parsing et éviter la boucle ci-dessous.
                       #skipinitialspace=False
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

    columns = colnames_by_table[name]
    if usecols is not None:
        columns = [colnames_by_table[name][k] for k in usecols]
    assert len(tab.columns) == len(columns)
    tab.columns = columns
    return tab


variables_de_gestion =  ['Utilisateur_Creation', 'DateCreation', 'DateCreationGMT',
       'Utilisateur_Modification', 'DateModification', 'DateModificationGMT',
       'Utilisateur_Suppression', 'DateSuppression', 'DateSuppressionGMT']


def read_configuration(name):
    file_name = 'Configuration_R_' + name
    output = read_bspp_table(file_name)
    for col in variables_de_gestion:
        if col in output.columns:
            del output[col]
    return output
