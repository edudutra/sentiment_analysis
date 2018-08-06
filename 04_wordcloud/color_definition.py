# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 10:00:25 2018

@author: eduardo.dutra
"""

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
        '#FF0000',  
        '#E21C00',  
        '#C63800',  
        '#AA5500',  
        '#8D7100',  
        '#718D00',  
        '#55AA00',  
        '#38C600',  
        '#1CE200',  
        '#00FF00'
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