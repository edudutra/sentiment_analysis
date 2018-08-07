# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 23:13:50 2018

@author: eduardo.dutra
"""

import math
#from textblob import TextBlob as tb
#import json
from glob import glob
#import csv
import re
import string
from wordcloud import WordCloud
#import itertools
from stopwords_pt import stopwords_pt
from nltk.tokenize import word_tokenize
from PIL import Image
import numpy as np
import pandas as pd
import multidict
import matplotlib.pyplot as plt
import os

# Define limits for negative and positive sentiment


files = glob('../data/sentiment/sentimento*.csv')
dfs = [pd.read_csv(fp, sep=';',quotechar='"', header=None, names=['sentiment', 'tweet', 'tweet_english', 'columns', 'negative', 'neutral', 'positive', 'compound']).assign(candidate=os.path.basename(fp).split('.')[0].split('_')[1]) for fp in files]
df_total = pd.concat(dfs, ignore_index=True)
print (df_total)
             
df = df_total[['candidate', 'tweet', 'compound']]

df.loc[:,'tweet'] = df['tweet'].str.replace(r'@([A-Za-z0-9_]+)', '', regex=True)
df.loc[:,'tweet'] = df['tweet'].str.replace(r'http\S+', '', regex=True)
df.loc[:,'tweet'] = df['tweet'].str.replace(r'[^{}]+'.format(string.printable + 'áéíóúàèìòùâêîôûãõªº°äëïöüÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕªº°ÄËÏÖÜçÇ'), '', regex=True)
df.loc[:,'tweet'] = df['tweet'].str.replace(r'k+', '', regex=True, flags=re.IGNORECASE)
df.loc[:,'tweet'] = df['tweet'].str.replace(r' +', ' ', regex=True)

df.dropna(inplace=True)


sentiments = {'neutral' : {'start' : -.2, 'end' : .2},
          'negative' : {'start' : -1., 'end' : -.5},
          'positive' : {'start' : .5, 'end' : 1.},     
    }

dfs = [ df[(df['compound'] >= s[1]['start']) & (df['compound'] <= s[1]['end'])].assign(sentiment=s[0]) 
        for s 
        in sentiments.items()]

df = pd.concat(dfs)

df_concat = df.groupby(['candidate', 'sentiment']).tweet.apply(lambda x : '\n'.join(x))
df_concat = df_concat.reset_index()



sentiment_dataframes = {}
for i, row in df_concat.iterrows():
    print(row[1])
    print('\t{}: {}'.format(row[0], len(row[2])))
    tmp = pd.DataFrame(word_tokenize(row[2]), columns=['word']).assign(candidate=row[0])
    wordlist = sentiment_dataframes.get(row[1], [])
    wordlist.append( tmp.groupby(['candidate', 'word']).size().to_frame('frequency').reset_index() )
    sentiment_dataframes[row[1]] = wordlist
    
for s in sentiment_dataframes.items():
    tmp_df = pd.concat(s[1])
    tmp_df.index = np.arange(tmp_df.shape[0])
    sentiment_dataframes[s[0]] = tmp_df


for item in sentiment_dataframes.items():  
    print(item[0])
    df = item[1]
    df['total_words'] = df.groupby(['candidate']).frequency.transform(np.sum)
    df['n_containing'] = df.groupby(['word']).candidate.transform(np.size)
    df['tf'] = df['frequency']/df.total_words 
    df['idf'] = np.log( 8 / df.n_containing )
    df['tfidf'] = df.tf*df.idf
    df = df[df['tfidf'] != 0]

for item in sentiment_dataframes.items():  
    print(item[0])
    df = item[1]
    df['rank'] = df.groupby(['candidate'])['frequency'].rank(ascending=False)



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
        for file in files:
            candidate = os.path.basename(file).split('.')[0].split('_')[1]
            print(candidate)
            freqs = df[(df['candidate'] == candidate) & (df['rank'] > start) & (df['tfidf'] != 0)][['word', 'frequency']]
            
            df['rank'] = df[df['tfidf'] != 0].groupby(['candidate'])['frequency'].rank(ascending=False)
            df_plt = df[(df['candidate'] == candidate) & (df['rank'] > start) & (df['tfidf'] != 0)].sort_values([ 'candidate', 'frequency'], ascending=[True, False])[['candidate', 'word', 'frequency']].head(15)
            ax = df_plt.plot.barh(x='word', y='frequency', title='Top 15 {} words for {}'.format(item[0], candidate.upper()), figsize=(12,8))
            ax.invert_yaxis()
            fig = ax.get_figure()
            fig.savefig('../imagens/barh_tfidf_{}_{}_start_{}.png'.format(candidate, item[0], start))

           #freqs = df[(df['candidate'] == 'amoedo') & (df['rank'] > 0) & (df['tfidf'] != 0)][['word', 'frequency']]
            wordcloud = WordCloud(width=1200, height=1200, background_color="white", mask=brazil_mask,normalize_plurals=False)#,
                       #stopwords=stopwords_pt, font_path='/Library/Fonts/Times New Roman.ttf')
            wordcloud.generate_from_frequencies(to_multidict(freqs.values))
            plt.axis("off")
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.show()
            wordcloud.to_file('../imagens/tfidf_{}_{}_start_{}.png'.format(candidate, item[0], start))


"""
df = sentiment_dataframes['negative']
df['rank'] = df[df['tfidf'] != 0].groupby(['candidate'])['frequency'].rank(ascending=False)
df_plt = df[(df['rank'] <= 15) & (df['tfidf'] != 0)].sort_values([ 'candidate', 'frequency'], ascending=[True, False])[['candidate', 'word', 'frequency']]

df_pivot = pd.pivot_table(df_plt, values='frequency', columns=['candidate'], index=['word'], aggfunc=np.sum)
ax = df_pivot.plot(kind='barh', subplots=True, layout=(4, 2), figsize=(15, 10), sharex=False)
#ax.invert_yaxis()
fig = ax.get_figure()
fig.savefig('../imagens/barh.png')
"""