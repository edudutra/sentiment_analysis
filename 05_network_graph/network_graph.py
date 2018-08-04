#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 23:28:22 2018

@author: eduardodutra
"""

import csv
from glob import glob
import networkx as nx



candidatos = dict([])
full_word_list = []

for filename in glob('../data/frequency/pyspark*.csv'):
    print(filename)
    candidato = filename.split('_')[2].split('.')[0]
    with open(filename, newline='\r\n', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        data = dict(reader)
        del data['Word']
        candidatos[candidato] = data
        full_word_list = list(set(full_word_list + list(data.keys())))

#full_word_list = list(full_word_list.sort())

keys = list(candidatos.keys())
grafo = [['palavra']+keys]

for word in full_word_list:
    row = [word]
    for cand in candidatos:
        row.append(candidatos[cand].get(word,None))
    grafo.append(row)
    
with open('out/grafo.csv', 'w', encoding='utf-8') as f: 
    csv_out=csv.writer(f)
    csv_out.writerows(grafo)


G = nx.Graph()

for filename in glob('../data/frequency/pyspark*.csv'):
    print(filename)
    candidato = filename.split('_')[2].split('.')[0]
    G.add_node(candidato, candidate=candidato) 
    with open(filename, newline='\r\n', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        data = dict(reader)
        del data['Word']
        for linha in data.items():
            if int(linha[1]) >= 50:
                G.add_node(linha[0], candidate='') 
                G.add_edge(candidato, linha[0], frequency=linha[1], candidate=candidato) 


import matplotlib.pyplot as plt
# create number for each group to allow use of colormap
from itertools import count
# get unique groups

fig = plt.figure(frameon = False)
fig.set_size_inches(15, 10)
ax = plt.Axes(fig, [0., 0., 1., 1.], )
ax.set_axis_off()
fig.add_axes(ax)

groups = set(nx.get_node_attributes(G,'candidate').values())
list(groups)
mapping = dict(zip(sorted(groups),count()))
nodes = G.nodes()
colors = [mapping[G.node[n]['candidate']] for n in nodes]
sizes = [len(G[n])+2 for n in nodes]
labels=dict([n for n in enumerate(nodes)])

# drawing nodes and edges separately so we can capture collection for colobar
pos = nx.spring_layout(G)
ec = nx.draw_networkx_edges(G, pos, alpha=0.1)
nc = nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=colors, 
                            with_labels=True, node_size=sizes, cmap=plt.cm.jet)
lc = nx.draw_networkx_labels(G, pos)

#lc = nx.draw_networkx_labels(G,pos,labels,font_size=16)
plt.colorbar(nc)
plt.axis('off')
#plt.show()
plt.savefig('imagens/grafo.png', dpi = 300)
