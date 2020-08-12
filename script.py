from source_scraping import load_all, load_province
from topic_modelling import *

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.linear_model import SGDClassifier, SGDRegressor, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.multiclass import OneVsRestClassifier, OneVsOneClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score
from sklearn.utils import shuffle
from sklearn.svm import LinearSVC, SVC, SVR, LinearSVR

from xgboost import XGBClassifier, XGBRegressor
from matplotlib import pyplot as plt

import numpy as np
import pandas as pd

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input, Activation, ActivityRegularization
from tensorflow.keras.optimizers import SGD, Nadam, Adam, Adamax
from tensorflow.keras.regularizers import l1, l2, l1_l2
from tensorflow.keras.metrics import Precision, Recall, BinaryAccuracy, AUC

import os
import joblib

df = load_all(update_csv=True)
df = df[df['region'] != 'Quebec']

bin_clf = joblib.load('models/binary_rnd_clf')
ann = keras.models.load_model('models/multilabel_ann')
lda_model = LdaModel.load('models/lda')

lda_info = {
    'best_model' : lda_model,
    'id2word' : lda_model.id2word
}

import pandas as pd

csv_path = 'predictions.csv'

try: 
    preds = pd.read_csv(csv_path)
    preds = df.append(preds) # Newest articles first
    preds = preds.drop_duplicates(['source_full_text'], keep='last') # Will keep predicted instance of text
except:
    preds = df

def lda_preprocess(texts, lda_model, lda_dict, stop_words=stopwords.words('english'), allowed_postags=['NOUN', 'ADJ', 'VERB']):
    partially_processed = custom_preprocess(texts, stop_words=stop_words, allowed_postags=allowed_postags)
    corpus = form_corpus(partially_processed, lda_dict)
    texts_by_topic = [lda_model.get_document_topics(doc) for doc in corpus]
    processed_texts = []
    for topic_list in texts_by_topic:
        feature_list = np.zeros(len(lda_model.get_topics()))
        for index, value in topic_list:
            feature_list[index] = value
        processed_texts.append(feature_list)
    return np.array(processed_texts)

def geo_stop_words(df):
    flatten = lambda l: [item for sublist in l for item in sublist] # flatten code from stackoverflow...
    region_stop_words = set(flatten([reg.lower().split() for reg in df['region'].dropna()]))
    sub_region_stop_words = set(flatten([reg.lower().split() for reg in df['subregion'].dropna()]))
    geo_stop_words = region_stop_words.union(sub_region_stop_words)
    return geo_stop_words

stopwords = stopwords.words('english')
stopwords.extend(geo_stop_words(preds))
stopwords.append('Some parts of this page will not display.JavaScript is not available in this browser or may be turned off.')

texts = np.array(preds['source_full_text'])
x = lda_preprocess(texts, lda_model, lda_model.id2word, stop_words=stopwords)

intervention_confidences = bin_clf.predict_proba(x)[:, 1]
multilabel_predictions = ann.predict(x)

multi_confidences = []
predicted_labels = []

cats = np.array(['H', 'C', 'E'])

for bin_conf, multi_conf in zip(intervention_confidences, multilabel_predictions):    
    if bin_conf < 0.5:
        multi_confidences.append('')
        predicted_labels.append('')
    if bin_conf >= 0.5:
        
        multi_confidences.append(multi_conf)
        predictions = np.array(multi_conf > 0.5)
        
        if np.count_nonzero(predictions):
            predicted_labels.append(cats[predictions])
        else: # If the ann thinks there are no interventions
            predicted_labels.append(cats[np.argmax(multi_conf)])

h_confidences = []
c_confidences = []
e_confidences = []

for conf in multi_confidences:
    if conf != '':
        h_confidence, c_confidence, e_confidence  = conf
    else:
        h_confidence, e_confidence, c_confidence = ('', '', '')
        
    h_confidences.append(h_confidence)
    c_confidences.append(c_confidence)
    e_confidences.append(e_confidence)

stringify = lambda arr: ', '.join(arr)
predicted_labels = list(map(stringify, predicted_labels))

preds['predicted_labels'] = predicted_labels
preds['intervention_confidence'] = intervention_confidences
preds['health_confidence'] = h_confidences
preds['containment_confidence'] = c_confidences
preds['economic_confidence'] = e_confidences

preds.to_csv(csv_path)