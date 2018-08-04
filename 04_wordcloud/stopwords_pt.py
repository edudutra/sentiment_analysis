# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 22:56:07 2018

@author: eduardo.dutra
"""

import urllib.request, json 
from nltk.corpus import stopwords
from string import punctuation

with urllib.request.urlopen("https://raw.githubusercontent.com/edudutra/stopwords-pt/master/stopwords-pt.json") as url:
    stopwords_pt = json.loads(url.read().decode())

stopwords_custom = [
        "https",
        "eleições",
        "das",
        "nas",
        "para",
        "que",
        "co",
        "não",
        "só",
        "ele",
        "como",
        "em",
        "esse",
        "por",
        "essa",
        "é",
        "...",
        "vai",
        "pra",
        "ser",
        "agora",
        "''",
        "``",
        "q",
        "vamos",
        "vamo",
        "ainda",
        "sobre",
        "diz",
        "pode",
        "ter",
        "tá",
        "pq",
        "Mexico",
        "vc",
        "Sporting",
        "México",
        "acho",
        "ganhar",
        "chegar",
        "chegando",
        "deixar",
        "fica"
        ,"ta"
        ,"tô"
        ,"vcs"
        ,"vou"
        ,"né"
        ,"já"
        ,"to"
        ,"Lopez Obrador"
        ,"via YouTube"
        ,"via UOLPolitica"
        ,"UOL"
        ,"UOLPolitica"
        ,"vídeo YouTube"
        ,"disse"
        ,"Gostei vídeo"
        ,"pras"
        ,"agr"
        ,"Deu"
        ]

stopwords_pt = list(set(stopwords_pt + stopwords_custom + stopwords.words('portuguese') + list(punctuation)))
