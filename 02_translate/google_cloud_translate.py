#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import print_function
import json
import os
import re
from googleapiclient.discovery import build
from glob import glob



def service():
    return build('translate', 'v2',
    #        developerKey='AIzaSyB_FbE8zvRqrMZ9HrnsTuhRrJ1a7gfHmZE') #dani
    #        developerKey='AIzaSyBjuUZtFBum9XFSjoTKKV4k13cnUhDbL2M') #nelson
            developerKey='AIzaSyCadkSZaCcpNSdas2NYM9GjwA8KtjPzB8s') #overbug

def translate(service, text):

  return service.translations().list(
      source='pt',
      target='en',
      q=[text]
    ).execute()
  

def read_file(candidate):
    translations = []
    
    print('../data/concat/{}.json'.format(candidate))
    with open('../data/concat/{}.json'.format(candidate)) as f:
        for line in f:
            tweet = json.loads(line)
            if 'retweeted_status' in tweet:
                tweet = tweet['retweeted_status']
            if not any(d['id'] == tweet['id'] for d in translations):
                translations.append({
                            'id' : tweet['id'], 
                            'full_text': tweet['full_text']
                        })
    return translations

def clear_text(translations):
    for i, t in enumerate(translations):
        t['clear_text'] =  re.sub(r'http\S+', '', t['full_text'])
        t['clear_text'] =  re.sub(r'@([A-Za-z0-9_]+)', '', t['clear_text'])
    
        translations[i] = t
    return translations

def print_size(translations):
    soma = 0;
    for t in translations:
        soma += len(t['clear_text'])        
    print(t)

def translate_file(translations):
    continuar = True
    
    while(continuar):
        try:
            service = service()
            
            for i, t in enumerate(translations):
                if not 'english_text' in t:
                    translation = translate(service, t['clear_text'])
                    t['english_text'] = translation['translations'][0]['translatedText']
                    translations[i] = t
                    print(i)
            continuar = False
        except:
            print('Erro. Reconectando')
    return translations

def write_files(candidate, translations):
    with open('../data/translate/translated_{}.json'.format(candidate), 'w') as fout:
        json.dump(translations, fout)
    
    import csv
    
    keys = translations[0].keys()
    
    with open('../data/translate/translated_{}.csv'.format(candidate), 'w', encoding='utf8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(translations)

if __name__ == '__main__':

    # Maps candidate filename generated in tweetf0rm to candidate
    candidates = [
        ('7b2621ff416cd332cbb1e280e4b3a69e', 'alckmin'),
        ('d9e96914299f35e8043a5b4399ac1a15', 'amoedo'),
        ('6e8149dd7c3b262b25e8c3c01b6790ba', 'bolsonaro'),
        ('e233015f9c8e42382cb40b6b5c803c2e', 'ciro'),
        ('43055dde5ea0624dcc683d9d34344db8', 'eleicoes'),
        ('366e2b4ebef0f8841a045a7873c31eaf', 'manuela'),
        ('3df4a449ad99354857ad27b0290c8452', 'marina'),
        ('71dff241bf5e39c64fbdb0c2617e7683', 'meirelles'),
        ]
    
    # copy all files into one per candidate, with human readable name
    for candidate in candidates:
        with open('../data/concat/{}.json'.format(candidate[1]), 'w') as outfile:
            for file in glob('../data/eleicoes/2018070**/{}'.format(candidate[0])):
                with open(file) as infile:
                    for line in infile:
                        outfile.write(line)
    
    for candidate in candidates:
        translations = read_file(candidate)
        translations = clear_text(translations)
        print_size(translations)
        translations = translate_file(translations)
        write_files(candidate, translations)
        
