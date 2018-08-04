#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import print_function
import json
import os
import re
from googleapiclient.discovery import build

service = build('translate', 'v2',
#        developerKey='AIzaSyB_FbE8zvRqrMZ9HrnsTuhRrJ1a7gfHmZE') #dani
#        developerKey='AIzaSyBjuUZtFBum9XFSjoTKKV4k13cnUhDbL2M') #nelson
        developerKey='AIzaSyCadkSZaCcpNSdas2NYM9GjwA8KtjPzB8s') #overbug

def translate(text):

  return service.translations().list(
      source='pt',
      target='en',
      q=[text]
    ).execute()
  
CANDIDATE = 'amoedo'

translations = []

for filename in os.listdir(CANDIDATE):
    print('{}/{}'.format(CANDIDATE, filename))
    with open('{}/{}'.format(CANDIDATE, filename)) as f:
        for line in f:
            tweet = json.loads(line)
            if 'retweeted_status' in tweet:
                tweet = tweet['retweeted_status']
            if not any(d['id'] == tweet['id'] for d in translations):
                translations.append({
                            'id' : tweet['id'], 
                            'full_text': tweet['full_text']
                        })
            #t = translate(tweet.full_text)
            

for i, t in enumerate(translations):
    t['clear_text'] =  re.sub(r'http\S+', '', t['full_text'])
    t['clear_text'] =  re.sub(r'@([A-Za-z0-9_]+)', '', t['clear_text'])

    translations[i] = t


soma = 0;
for t in translations:
    soma += len(t['clear_text'])
    
print(t)

continuar = True

while(continuar):
    try:
        service = build('translate', 'v2',
#        developerKey='AIzaSyB_FbE8zvRqrMZ9HrnsTuhRrJ1a7gfHmZE') #dani
#        developerKey='AIzaSyBjuUZtFBum9XFSjoTKKV4k13cnUhDbL2M') #nelson
        developerKey='AIzaSyCadkSZaCcpNSdas2NYM9GjwA8KtjPzB8s') #overbug
        
        for i, t in enumerate(translations):
            if not 'english_text' in t:
                translation = translate(t['clear_text'])
                t['english_text'] = translation['translations'][0]['translatedText']
                translations[i] = t
                print(i)
        continuar = False
    except:
        print('Erro. Reconectando')


with open('result/translated_{}.json'.format(CANDIDATE, CANDIDATE), 'w') as fout:
    json.dump(translations, fout)

import csv

keys = translations[0].keys()

with open('result/translated_{}.csv'.format(CANDIDATE), 'w', encoding='utf8') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(translations)
    
    

translate('oi')
