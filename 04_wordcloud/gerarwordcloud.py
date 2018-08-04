# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 09:49:37 2018

@author: eduardo.dutra
"""

import csv
from glob import glob
import json
import re
from stopwords_pt import stopwords_pt
from nltk.tokenize import word_tokenize
import itertools
import operator
from wordcloud import WordCloud
from PIL import Image
import numpy as np
from color_definition import SimpleGroupedColorFunc, color_to_use, default_color
import math
import matplotlib.pyplot as plt

#%% Define limits for negative and positive sentiment

NEGATIVE_START = .0
NEGATIVE_END = .3

POSITIVE_START = .7
POSITIVE_END = 1.

#%% Load Files
candidates = [{'candidate' : candidato.split('_')[1].split('.')[0], 'filename' : candidato, 'type': candidato.split('.')[3]} for candidato in glob('../data/sentiment/sentimento*')]

for candidate in candidates:
    print('{}'.format(candidate))
    if candidate['type'] == 'csv':
        with open(candidate['filename'], newline='\r\n', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            data = list(reader)
            candidate['data'] = [{'full_text' : tweet[1], 'score' : (float(tweet[7])+1)/2 } for tweet in data]
    else:
        with open(candidate['filename']) as f:
            data = json.load(f)
            candidate['data'] = [{'full_text' : tweet['full_text'], 'score' : tweet['score']} for tweet in data]

#%% Clear text
            
re_twitter_username = re.compile(r'@([A-Za-z0-9_]+)')
re_spaces = re.compile(r' +')
for candidate in candidates:
    for i, line in enumerate(candidate['data']):
        candidate['data'][i]['full_text'] = re.sub(re_twitter_username, '', line['full_text'])          
        candidate['data'][i]['full_text'] = re.sub(re_spaces, ' ', line['full_text'])

#%% Join texts by sentiment

for candidate in candidates:
    candidate['text_positive'] = '\n'.join( [tweet['full_text'] for tweet in candidate['data'] if tweet['score'] >= POSITIVE_START and tweet['score'] <= POSITIVE_END ] )
    candidate['text_negative'] = '\n'.join( [tweet['full_text'] for tweet in candidate['data'] if tweet['score'] >= NEGATIVE_START and tweet['score'] <= NEGATIVE_END ] )
    candidate['text'] = '\n'.join( [tweet['full_text'] for tweet in candidate['data']] )


#%% Calculate mean scores per word
def calculate_score_palavras(data):
    score_palavras_full = []
    
    for i, tweet in enumerate(data):
        #print((i, tweet['score']))
        for palavra in word_tokenize(tweet['full_text'].lower()):
            score_palavras_full.append( (i, tweet['score'], palavra) ) 
        
    score_palavras_full = sorted(score_palavras_full, key=lambda tup: tup[2])
    
    def accumulate(l):
        it = itertools.groupby(l, operator.itemgetter(2))
        for key, subiter in it:
            temp_list =[item[1] for item in subiter]
            yield key, sum(temp_list)/len(temp_list)
           
    score_palavras = list(accumulate(score_palavras_full))
    score_palavras_neg = list(accumulate([tweet for tweet in score_palavras_full if tweet[1] >= NEGATIVE_START and tweet[1] <= NEGATIVE_END]))
    score_palavras_pos = list(accumulate([tweet for tweet in score_palavras_full if tweet[1] >= POSITIVE_START and tweet[1] <= POSITIVE_END]))

    return score_palavras, score_palavras_pos, score_palavras_neg

for candidate in candidates:
    candidate['score_palavras'], candidate['score_palavras_pos'], candidate['score_palavras_neg'] = calculate_score_palavras(candidates[0]['data'])
    
#%% Define function for generating wordclouds

def generate_wordclouds(candidate):

    texts = {'total': candidate['text'], 'positive': candidate['text_positive'], 'negative' : candidate['text_negative']}
    scores = {'total': candidate['score_palavras'], 'positive': candidate['score_palavras_pos'], 'negative' : candidate['score_palavras_neg']}
    
    brazil_mask = np.array(Image.open("brazil_mask.png"))
    
    colors = {}
    for score in scores.items():
        colors[score[0]] = SimpleGroupedColorFunc({p[0] : color_to_use[math.floor(p[1]*9.99)] for p in score[1]}, default_color)

    wordcloud = WordCloud(width=1200, height=1200, background_color="white", mask=brazil_mask,
               stopwords=stopwords_pt)


    for text in texts.items():
        wordcloud_total=wordcloud.generate(text[1])
        wordcloud_total.recolor(color_func=colors[text[0]])
        
        plt.axis("off")
        plt.imshow(wordcloud_total, interpolation="bilinear")
        plt.show()
        
        #image_total = wordcloud_total.to_image()
        #image_total.show()
        wordcloud_total.to_file('../imagens/{}_{}_{}.png'.format('pyspark' if candidate['type']=='csv' else 'azure', candidate['candidate'], text[0]))

    #generate CSV
    if candidate['type']=='csv':
        freq = wordcloud.process_text(texts['total'])
    
        with open('../data/frequency/pyspark_frequency_{}.csv'.format(candidate['candidate']), 'w', encoding='utf-8') as f:  # Just use 'w' mode in 3.x
            csv_out=csv.writer(f)
            csv_out.writerow(['Word','Count'])
            for key in freq.keys():
                csv_out.writerow((key,freq[key]))


#%% Iterate and generate wordclouds
        
for candidate in candidates:
    generate_wordclouds(candidate) 

           

