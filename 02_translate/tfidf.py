#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  5 00:15:59 2018

@author: eduardodutra
"""

import math
#from textblob import TextBlob as tb
import json
from glob import glob
import csv
import re
import string
from wordcloud import WordCloud
import itertools
import math
from stopwords_pt import stopwords_pt
from nltk.tokenize import word_tokenize
from PIL import Image
import numpy as np
import pandas as pd
import multidict
import matplotlib.pyplot as plt


# Define limits for negative and positive sentiment

NEGATIVE_START = .0
NEGATIVE_END = .25

POSITIVE_START = .75
POSITIVE_END = 1.


# exclude the tweets with the following terms
exclude_terms = [r'\bcuando\b', r'\by\b', r'\ben\b', r'\bla\b', r'\blas\b', r'\bpaula amoedo\b', r'\bsporting\b', r'\blo\b', r'\byo\b']
re_exclude = re.compile(r'|'.join(exclude_terms), re.IGNORECASE)

candidates = [{'candidate' : candidato.split('_')[1].split('.')[0], 'filename' : candidato, 'type': candidato.split('.')[3]} for candidato in glob('../data/sentiment/sentimento*.csv')]

for candidate in candidates:
    print('{}'.format(candidate))
    if candidate['type'] == 'csv':
        with open(candidate['filename'], newline='\r\n', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            data = list(reader)
            candidate['data'] = [{'full_text' : tweet[1], 'score' : (float(tweet[7])+1)/2 } for tweet in data if not re.search(re_exclude, tweet[1])]
    else:
        with open(candidate['filename']) as f:
            data = json.load(f)
            candidate['data'] = [{'full_text' : tweet['full_text'], 'score' : tweet['score']} for tweet in data if not re.search(re_exclude, tweet['full_text'])]

# Clear text
            
re_twitter_username = re.compile(r'@([A-Za-z0-9_]+)')
re_spaces = re.compile(r' +')
re_link = re.compile(r'http\S+')
re_emoji = re.compile(r'[^{}]+'.format(string.printable + 'áéíóúàèìòùâêîôûãõªº°äëïöüÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕªº°ÄËÏÖÜçÇ'))

regex = [re_twitter_username, re_link, re_emoji] 

for candidate in candidates:
    for i, line in enumerate(candidate['data']):
        for r in regex:
            candidate['data'][i]['full_text'] = re.sub(r, '', line['full_text']) 
        candidate['data'][i]['full_text'] = re.sub(re_spaces, ' ', line['full_text']) 
            
# Join texts by sentiment

for candidate in candidates:
    candidate['text'] = {}
    candidate['text']['positive'] = '\n'.join( [tweet['full_text'].lower() for tweet in candidate['data'] if tweet['score'] >= POSITIVE_START and tweet['score'] <= POSITIVE_END ] )
    candidate['text']['negative'] = '\n'.join( [tweet['full_text'].lower() for tweet in candidate['data'] if tweet['score'] >= NEGATIVE_START and tweet['score'] <= NEGATIVE_END ] )
    candidate['text']['neutral'] = '\n'.join( [tweet['full_text'].lower() for tweet in candidate['data']] )
    #candidate['text_positive'] = '\n'.join( [tweet['full_text'].lower() for tweet in candidate['data'] if tweet['score'] >= POSITIVE_START and tweet['score'] <= POSITIVE_END ] )
    #candidate['text_negative'] = '\n'.join( [tweet['full_text'].lower() for tweet in candidate['data'] if tweet['score'] >= NEGATIVE_START and tweet['score'] <= NEGATIVE_END ] )
    #candidate['text'] = '\n'.join( [tweet['full_text'].lower() for tweet in candidate['data']] )

sentiments = ['neutral', 'positive', 'negative']

    
textlist = {}
for sentiment in sentiments:
    textlist[sentiment] = [{'candidate': c['candidate'], 'text': c['text'][sentiment]} for c in candidates]



sentiment_dataframes = {}
for sentiment in sentiments:
    wordlist = []
    print(sentiment)
    for text in textlist[sentiment]:
        print('\t{}: {}'.format(text['candidate'], len(text['text'])))
        tmp = pd.DataFrame(word_tokenize(text['text']), columns=['word'])
        tmp['candidate'] = text['candidate']
        wordlist.append( tmp.groupby(['candidate', 'word']).size().to_frame('frequency').reset_index() )
    tmp_df = pd.concat(wordlist)
    tmp_df.index = np.arange(tmp_df.shape[0])
    sentiment_dataframes[sentiment] = tmp_df


for item in sentiment_dataframes.items():  
    print(item[0])
    df = item[1]
    df['total_words'] = df.groupby(['candidate']).frequency.transform(np.sum)
    df['n_containing'] = df.groupby(['word']).candidate.transform(np.size)
    df['tf'] = df['frequency']/df.total_words 
    df['idf'] = np.log( len(candidates) / df.n_containing )
    df['tfidf'] = df.tf*df.idf
    df = df[df['tfidf'] != 0]
    
#for item in sentiment_dataframes.items():  
#    print(item[0])
#    df = item[1]
#    df['rank'] = df.groupby(['candidate'])['frequency'].rank(ascending=False)


#amoedo = df[(df['candidate'] == 'amoedo') &(df['rank'] > 0) & (df['tfidf'] != 0)].sort_values([ 'tfidf', 'candidate'], ascending=[False, True]).head(30)


#df['rank'] = 
#df.groupby(['candidate'])['frequency'].rank(ascending=False)

#df.index = np.arange(df.shape[0])

def to_multidict(items):
    fullTermsDict = multidict.MultiDict()
    for item in items:
        fullTermsDict.add(item[0], item[1])
    return fullTermsDict

#to_multidict(freqs.head(5).values)  

#for item in freqs.head(5).values:
#    print('{}: {}'.format(item[0], item[1]))

brazil_mask = np.array(Image.open("brazil_mask.png"))
for item in sentiment_dataframes.items():  
    print(item[0])
    df = item[1]
    for start in list(range(0,0+1,5)):
        for candidate in candidates:
            print(candidate['candidate'])
            freqs = df[(df['candidate'] == candidate['candidate']) & (df['rank'] > start) & (df['tfidf'] != 0)][['word', 'frequency']]
            
            df['rank'] = df[df['tfidf'] != 0].groupby(['candidate'])['frequency'].rank(ascending=False)
            df_plt = df[(df['candidate'] == candidate['candidate']) & (df['rank'] > start) & (df['tfidf'] != 0)].sort_values([ 'candidate', 'frequency'], ascending=[True, False])[['candidate', 'word', 'frequency']].head(15)
            ax = df_plt.plot.barh(x='word', y='frequency', title='Top 15 {} words for {}'.format(item[0], candidate['candidate'].upper()), figsize=(12,8))
            ax.invert_yaxis()
            fig = ax.get_figure()
            fig.savefig('../imagens/barh_tfidf_{}_{}_start_{}.png'.format(candidate['candidate'], item[0], start))

           #freqs = df[(df['candidate'] == 'amoedo') & (df['rank'] > 0) & (df['tfidf'] != 0)][['word', 'frequency']]
            wordcloud = WordCloud(width=1200, height=1200, background_color="white", mask=brazil_mask,normalize_plurals=False)#,
                       #stopwords=stopwords_pt, font_path='/Library/Fonts/Times New Roman.ttf')
            wordcloud.generate_from_frequencies(to_multidict(freqs.values))
            plt.axis("off")
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.show()
            wordcloud.to_file('../imagens/tfidf_{}_{}_start_{}.png'.format(candidate['candidate'], item[0], start))


