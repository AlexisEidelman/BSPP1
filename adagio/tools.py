# -*- coding: utf-8 -*-
"""
@author: alexis
"""

def translate_id_into_label(suffixe, tab, referentiel, method='columns'):
    ''' suffixe c'est le nom de la variable qui est précédé par Id, Abrege
        ou Libelle 
    '''
    if method == 'columns':
        translation = dict()
        for idx, row in referentiel.iterrows():
            translation[row['Id' + suffixe]] = row['Libelle' + suffixe]        
        return tab.rename(columns=translation)
    else:
        tab = tab.merge(referentiel[['Id' + suffixe, 'Libelle' + suffixe]],
            on='Id' + suffixe)
        del tab['Id' + suffixe]
        return tab.rename(columns={'Libelle' + suffixe: suffixe})
    
