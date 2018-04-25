'''
Created on 26-Feb-2018

@author: Vishnu
'''

from pymongo import MongoClient
import spacy
from textblob import TextBlob
import string
import random
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

lemma = WordNetLemmatizer()
stopword_set = set(stopwords.words("english"))
exclude = set(string.punctuation)
nlp = spacy.load('en')

def preprocess(raw_text):
    lemmatized = [lemma.lemmatize(i) for i in raw_text.split()]
    raw_text = ' '.join(lemmatized)
    raw_text = raw_text.lower()
    words = raw_text.split()
    meaningful_words = [w for w in words if w not in stopword_set]
    cleaned_word_list = " ".join(meaningful_words)
    cleaned_query = ''.join(ch for ch in cleaned_word_list if ch not in exclude)
    return cleaned_query

def clean(raw_text):
    raw_text = raw_text.lower()
    cleaned_query = ''.join(ch for ch in raw_text if ch not in exclude)
    return cleaned_query


host = "mongodb://ezio:hashedPassword_123@ds141232.mlab.com:41232/chatbotplatform"
db_client = MongoClient(host, port=41232)

fallback = ['Sorry, could you say that again?', 'Sorry, can you say that again?', 
            'Can you say that again?', "Sorry, I didn't get that.", 
            'Sorry, what was that?', 'Say that again?',
            "I didn't get that.", "Please rephrase your question."]

def Similar(query):
    text = TextBlob(query)
    data = list(db_client.chatbotplatform.intents.find({'chatBotId': '5a68d6d2f4f60e3eabcf566e'},
                                                       {'mappings':1, 'intentId': 1}))
    list_data = [list(i['mappings'].keys()) for i in data if 'mappings' in i and type(i['mappings']) == dict]
    flat_list = [item for sublist in list_data for item in sublist]
    if len(query.split())>2:
        lang = text.detect_language()
        if lang == 'en':
            questn = query
        else:
            translated = text.translate(to='en')
            questn = str(translated)
    else:
        querynew = query + ' ' + '.' + ' ' + '.'
        textnew = TextBlob(querynew)
        lang = textnew.detect_language()
        if lang == 'en':
            questn = clean(querynew)
        else:
            translated = textnew.translate(to='en')
            questn = str(translated)
            questn = clean(questn)
    list_indx = []
    for indx, i in enumerate(flat_list):
        dict_indx = {}
        dict_indx['index'] = indx
        dict_indx['similarity'] = nlp(preprocess(questn)).similarity(nlp(preprocess(i)))        
        if dict_indx['similarity'] > .7:
            list_indx.append(dict_indx)
    try:
        refined = max(range(len(list_indx)), key=lambda index: list_indx[index]['similarity'])
        ind = list_indx[refined]['index']
        similar = flat_list[ind]
        result = []
        for j in data:
            if 'mappings' in j and type(j['mappings']) == dict and similar in j['mappings']:
                result_dict = {}
                result_dict['response'] = similar
                result_dict['intentId'] = j['intentId']
                result.append(result_dict)
    except:
        result = [{'response': 'No Match Found', 'intentId': ''}]
    data_resp = list(db_client.chatbotplatform.mappings.find({'chatBotId': '5a68d6d2f4f60e3eabcf566e', 'intentResolvedId': str(result[0]['intentId'])}))
    if len(data_resp) > 0:
        respo = data_resp[0]['response']
        responses = [i['value'] for i in respo if i['type']==0]
        final_response = '.'.join(responses)
    else:
        final_response = random.choice(fallback)
    try:
        final_response = TextBlob(final_response)
        if lang != 'en':
            output = final_response.translate(to='zh-TW')
            output = str(output)
            return output
        else:
            output = str(final_response)
            return output
    except:
        output = str(final_response)
        return output
