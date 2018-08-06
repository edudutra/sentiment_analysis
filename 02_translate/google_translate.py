# -*- coding: utf-8 -*-

from googletrans import Translator
import json
from glob import glob
import os
import re
import string

translator = Translator()

#translation = translator.translate(['Oi.', 'Bom Dia', 'Como vai'], src='pt', dest='en')
#print(translation.extra_data)
#translator.translate('안녕하세요.', dest='ja')
#translator.translate('veritas lux mea', src='la')

translations = translator.translate(['Oi.', 'Bom Dia', 'Como vai'], src='pt', dest='en')
for translation in translations:
    print(translation.origin, ' -> ', translation.text)

# Maps candidate filename generated in tweetf0rm to candidate
candidates = {
    '7b2621ff416cd332cbb1e280e4b3a69e' : 'alckmin',
    'd9e96914299f35e8043a5b4399ac1a15' : 'amoedo',
    '6e8149dd7c3b262b25e8c3c01b6790ba' : 'bolsonaro',
    'e233015f9c8e42382cb40b6b5c803c2e' : 'ciro',
    '43055dde5ea0624dcc683d9d34344db8' : 'eleicoes',
    '366e2b4ebef0f8841a045a7873c31eaf' : 'manuela',
    '3df4a449ad99354857ad27b0290c8452' : 'marina',
    '71dff241bf5e39c64fbdb0c2617e7683' : 'meirelles',
}
    
all_tweets = dict({})

for file in glob('../data/eleicoes/2018070/**'):
    print(file)
    filename = os.path.basename(file)
    tweets = []
    with open(file) as f:
        for line in f:
            tweet = json.loads(line)
            tweets.append(tweet)
    all_tweets[candidates[filename]] = all_tweets.get(candidates[filename], []) + tweets
    #break

to_translate = []
for candidate in all_tweets.items():
    to_translate = to_translate + [
            (t['full_text'] if 'retweeted_status' not in t else t['retweeted_status']['full_text'], 
             t['id'] if 'retweeted_status' not in t else t['retweeted_status']['id']) 
            for t in candidate[1]
            ]

def clear_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^{}]+'.format(string.printable + 'áéíóúàèìòùâêîôûãõªº°äëïöüÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕªº°ÄËÏÖÜçÇ'), '', text)
    text = re.sub(r'@([A-Za-z0-9_]+)', '', text)          
    text = re.sub(r' +', ' ', text)
    return text

    
to_translate_clear = [clear_text(t[0]) for t in list(set(to_translate))]


#translations = translator.translate(to_translate_clear[336], src='pt', dest='en')

translations = []

for i, item in enumerate(to_translate_clear):
    print('{}/{}'.format(i, len(to_translate_clear)))
    try:
        translation = translator.translate(item, src='pt', dest='en')
        translations.append(translation)
    except ValueError:
        print('Erro {}'.format(i))
        translations.append(None)

count = 0
erros = [i for i, t in enumerate(translations) if t is None]
while len(erros) > 0:
    count = count + 1
    print('Tentativa {} - Erros {}'.format(count, len(erros)))
    for i in erros:
        print('{}/{}'.format(i,len(erros)))
        try:
            translations[i] = translator.translate(to_translate_clear[i], src='pt', dest='en')
        except ValueError:
            print('Erro {}'.format(i))
    erros = [i for i, t in enumerate(translations) if t is None]
            
            
        
