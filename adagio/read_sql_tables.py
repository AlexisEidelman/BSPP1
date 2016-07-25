# -*- coding: utf-8 -*-
"""
Created on Sat Jul 23 18:56:19 2016

@author: aeidelman
"""


import os
import io

path_data_sql = '/home/sgmap/data/BSPP/tables1'
path_sql = os.path.join(path_data_sql, '02-TABLES.sql') 

with io.open(path_sql, encoding='utf16') as f:
    sql_text = f.read()

for to_remove in ['SET ANSI_NULLS ON', 'GO', 'SET ANSI_NULLS ON',
                  'SET QUOTED_IDENTIFIER ON', 'SET ANSI_PADDING ON',
                  'SET ANSI_PADDING OFF', ') ON [FG_ADG]', '(']:
    sql_text = sql_text.replace('\n' + to_remove, '')
sql_text.replace('\n\n', '\n')

by_bloc = sql_text.split('/******')

parsed_sql = dict()
def clean_name(line):
    name = line[len('CREATE TABLE '):-1]
    assert len(name.split('].[')) == 2
    name = name.replace(']', '')
    name = name.replace('[', '')
    name = name.replace('.', '_')
    return name

def clean_var(line):
    var = line[1:] #on retire le '\t'
    assert var[0] == '['
    var = var[1:]
    if '] [' in var:
        var = var.split('] [')[0]
    elif '] ASC' in var:
        var = var[:-len('] ASC')]
    else:
        assert ']  AS (' in var
        # on oublie le As parce que quand on regarde
        # ca n'apporte pas grand chose
        var = var.split(']  AS (')[0]
    if var != 'Id Exception':
        assert ' ' not in var
    return var
    
pased_sql = dict()
for bloc in by_bloc:
    name = ''
    variables = list()
    for line in bloc.splitlines():
        if line == '' or 'ASC' in line:
            continue
        if 'CREATE TABLE' in line:
            name = clean_name(line)
        if line[0] == '\t':
            variables.append(clean_var(line))
    parsed_sql[name] = variables
