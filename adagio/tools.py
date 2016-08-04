# -*- coding: utf-8 -*-
"""
@author: alexis
"""

def translate_id_into_label(suffixe, tab, referentiel, method='merge',
                            other_cols=None):
    ''' suffixe c'est le nom de la variable qui est précédé par Id, Abrege
        ou Libelle 
    '''
    if method == 'columns':
        if other_cols is not None:
            raise Exception("cannot use others cols with this method")
        translation = dict()
        for idx, row in referentiel.iterrows():
            translation[row['Id' + suffixe]] = row['Libelle' + suffixe]        
        return tab.rename(columns=translation)
    else:
        variables_en_jeu = ['Id' + suffixe, 'Libelle' + suffixe]
        if other_cols is not None:
            assert isinstance(other_cols, list)
            variables_en_jeu += other_cols
        tab = tab.merge(referentiel[variables_en_jeu],
                        on='Id' + suffixe)
        del tab['Id' + suffixe]
        return tab.rename(columns={'Libelle' + suffixe: suffixe})
    
