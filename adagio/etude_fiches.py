# -*- coding: utf-8 -*-
"""
Created on Sat Aug 20 11:26:05 2016

@author: aeidelman
"""
import pandas as pd
import vincent
 
from appels import FicheDecisionnelle

Fiche = FicheDecisionnelle(None)
del Fiche['IdIntervention']

Fiche['Date'] = pd.to_datetime(Fiche['Date'])
Fiche.set_index('Date', inplace=True)

test = Fiche
test['nb'] = 1

import matplotlib.pyplot as plt

for i, group in test.groupby(["Categorie", "Pathologie"]):
    plt.figure()
#    import pdb
#    pdb.set_trace()
    print(len(group))
    group.resample('1D').sum().plot(title=str(i))

xxx
#Create a vincent line plot, and add your data. Vincent handles the translation
#of Pandas/Python datetimes to javascript epoch time.
vis = vincent.Line(Fiche.Valide.astype(int))
vis.tabular_data(Fiche.Valide.astype(int), axis_time='day')

#Add interpolation to make our fake data look nice
vis + ({'value': 'basis'}, 'marks', 0, 'properties', 'enter', 'interpolate')

#Make the visualization a bit wider, and add axis titles
vis.update_vis(width=700, height=300)
vis.axis_titles(x='Date', y='group')
vis.legend(title='GOOG vs AAPL')

vis.to_json('vega.json', html_out=True)