# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 23:45:56 2018

@author: eduardo.dutra
"""

CANDIDATE = 'eleicoes'

#%% Imports
import json
from wordcloud import WordCloud
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
#from nltk.tokenize import sent_tokenize
from stopwords_pt import stopwords_pt
import math
import itertools
import operator
import re
import csv

#%% Color Class
class SimpleGroupedColorFunc(object):
    """Create a color function object which assigns EXACT colors
       to certain words based on the color to words mapping

       Parameters
       ----------
       color_to_words : dict(str -> list(str))
         A dictionary that maps a color to the list of words.

       default_color : str
         Color that will be assigned to a word that's not a member
         of any value from color_to_words.
    """

    def __init__(self, word_to_color, default_color):
        self.word_to_color = word_to_color
 
        self.default_color = default_color

    def __call__(self, word, **kwargs):
        return self.word_to_color.get(word.lower(), self.default_color)


#%% Define limits for negative and positive sentiment

NEGATIVE_START = .0
NEGATIVE_END = .3

POSITIVE_START = .7
POSITIVE_END = 1.

#%% Load File

with open('data/sentimento_{}.json'.format(CANDIDATE)) as f:
    data = json.load(f)

#%% Clear text
twitter_username_re = re.compile(r'@([A-Za-z0-9_]+)')

for i, line in enumerate(data):
    data[i]['full_text'] = re.sub(twitter_username_re, '', line['full_text'])

#%% Join texts by sentiment
    
text_positive = '\n'.join( [tweet['full_text'] for tweet in data if tweet['score'] >= POSITIVE_START and tweet['score'] <= POSITIVE_END ] )
text_negative = '\n'.join( [tweet['full_text'] for tweet in data if tweet['score'] >= NEGATIVE_START and tweet['score'] <= NEGATIVE_END ] )
text = '\n'.join( [tweet['full_text'] for tweet in data] )

#%% Tokenize
#sentencas = sent_tokenize(text)
palavras = word_tokenize(text.lower())

stopwords = stopwords_pt

palavras_sem_stopwords = [palavra for palavra in palavras if palavra not in stopwords]

#%% Calculate mean scores per word
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

#%% Instantiate wordcloud       

brazil_mask = np.array(Image.open("brazil_mask.png"))
    
wordcloud = WordCloud(width=1200, height=1200, background_color="white", mask=brazil_mask,
               stopwords=stopwords)

#%% Change Colors
default_color = 'grey'

colors = [
        '#00FF00',  
        '#38FF00',
        '#71FF00', 
        '#AAFF00', 
        '#E2FF00', 
        '#FFE200', 
        '#FFAA00', 
        '#FF7100', 
        '#FF3800', 
        '#FF0000'
]

colors2 = [  
        '#00FF00',  
        '#1CE200',  
        '#38C600',  
        '#55AA00',  
        '#718D00',  
        '#8D7100',  
        '#AA5500',  
        '#C63800',  
        '#E21C00',  
        '#FF0000'
]
red_and_green = [  
        '#00FF00',  
        '#00FF00',  
        '#00FF00',  
        '#00FF00',  
        '#00FF00',  
        '#FF0000',  
        '#FF0000',  
        '#FF0000',  
        '#FF0000',  
        '#FF0000'
]

color_to_use = colors2

grouped_color_func = SimpleGroupedColorFunc({p[0] : color_to_use[math.floor(p[1]*9.99)] for p in score_palavras}, default_color)
grouped_color_func_pos = SimpleGroupedColorFunc({p[0] : color_to_use[math.floor(p[1]*9.99)] for p in score_palavras_pos}, default_color)
grouped_color_func_neg = SimpleGroupedColorFunc({p[0] : color_to_use[math.floor(p[1]*9.99)] for p in score_palavras_neg}, default_color)

#%% Save location and prefix

prefix = 'imagens/azure_{}'.format(CANDIDATE)

#%% Negative Cloud
# generate word cloud
wordcloud_neg=wordcloud.generate(text_negative)
wordcloud_neg.recolor(color_func=grouped_color_func_pos)

plt.axis("off")
plt.imshow(wordcloud_neg, interpolation="bilinear")
plt.show()

#image_neg = wordcloud_neg.to_image()
#image_neg.show()
wordcloud_neg.to_file(prefix + '_negative.bmp')

#%% Positive Cloud

wordcloud_pos=wordcloud.generate(text_positive)
wordcloud_pos.recolor(color_func=grouped_color_func_neg)
# Display the generated image:
# the matplotlib way:
plt.axis("off")
plt.imshow(wordcloud_pos, interpolation="bilinear")
plt.show()
# The pil way (if you don't have matplotlib)
wordcloud_pos.to_file(prefix + '_positive.bmp')
#image_pos = wordcloud_pos.to_image()
#image_pos.show()


#%% General Cloud

# generate word cloud
wordcloud_total=wordcloud.generate(text)
wordcloud_total.recolor(color_func=grouped_color_func)

plt.axis("off")
plt.imshow(wordcloud_total, interpolation="bilinear")
plt.show()

#image_total = wordcloud_total.to_image()
#image_total.show()
wordcloud_total.to_file(prefix + '_total.bmp')

#%% Write CSVs

freq = wordcloud.process_text(text)

with open('out/azure_frequency_{}.csv'.format(CANDIDATE), 'w', encoding='utf-8') as f:  # Just use 'w' mode in 3.x
    csv_out=csv.writer(f)
    csv_out.writerow(['Word','Count'])
    for key in freq.keys():
        csv_out.writerow((key,freq[key]))

