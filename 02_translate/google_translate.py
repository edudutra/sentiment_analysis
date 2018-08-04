from googletrans import Translator
import json
from glob import glob
import os

translator = Translator()

translation = translator.translate(['Oi.', 'Bom Dia', 'Como vai'], src='pt', dest='en')
print(translation.extra_data)
translator.translate('안녕하세요.', dest='ja')
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

for file in glob('../data/eleicoes/**/**'):
    print(file)
    filename = os.path.basename(file)
    tweets = []
    with open(file) as f:
        for line in f:
            tweet = json.loads(line)
            tweets.append(tweet)
    all_tweets[candidates[filename]] = all_tweets.get(candidates[filename], []) + tweets


for candidate in all_tweets.items():
    to_translate = [
            (t['full_text'] if 'retweeted_status' not in t else t['retweeted_status']['full_text'], 
             t['id'] if 'retweeted_status' not in t else t['retweeted_status']['id']) 
            for t in candidate[1]
            ]
    
to_translate = list(set(to_translate))

translations = []

for item in to_translate:
    print(item[0])
    translation = translator.translate(item[0], src='pt', dest='en')
    translations.append(translation)
    
x = translator.translate("""Até às eleições, as redes sociais serão um show memes protagonizados por pseudos jornalistas! 
Tem historiador da Wikipédia, Robô psicográfico, até "Cristo"refugiou- se para não olhar esta vergonha!
#BolsonaroNaGloboNews #SomosTodosBolsonaro""", src='pt', dest='en')



# copy all files into one per candidate, with human readable name
for candidate in candidates:
    with open('../data/concat/{}.json'.format(candidate[0]), 'w') as outfile:
        for file in glob('../data/eleicoes/**/{}'.format(candidate[0])):
            with open(file) as f:
                for line in f:
                    tweet = json.loads(line)
                    tweets.append(tweet)
                    
                    if 'retweeted_status' in tweet:
                        tweet = tweet['retweeted_status']
                    if not any(d['id'] == tweet['id'] for d in translations):
                        translations.append({
                                    'id' : tweet['id'], 
                                    'full_text': tweet['full_text']
                                })

    
    for candidate in candidates:
        translations = read_file(candidate)
        translations = clear_text(translations)
        print_size(translations)
        translations = translate_file(translations)
        write_files(candidate, translations)
        
