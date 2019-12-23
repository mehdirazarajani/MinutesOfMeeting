# import required packages

import pandas as pd 
import numpy as np
import os, gc, time, warnings
import itertools    

from scipy import sparse
import scipy.stats as ss
from scipy.sparse import csr_matrix, hstack, vstack

import matplotlib.pyplot as plt, matplotlib.gridspec as gridspec 
import seaborn as sns
from wordcloud import WordCloud ,STOPWORDS
from PIL import Image
import matplotlib_venn as venn
import pydot, graphviz
from IPython.display import Image

import string, re, nltk, collections
from nltk.util import ngrams
from nltk.corpus import stopwords
import spacy
from nltk import pos_tag
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer 
from nltk.tokenize import word_tokenize
from nltk.tokenize import TweetTokenizer   

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, HashingVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_X_y, check_is_fitted
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn import metrics
from sklearn.feature_selection import SelectFromModel
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split

import tensorflow as tf
import keras.backend as K
from keras.models import Model, Sequential
from keras.utils import plot_model
from keras.layers import Input, Dense, Embedding, SpatialDropout1D, concatenate, BatchNormalization
from keras.layers import GRU, LSTM, Bidirectional, GlobalAveragePooling1D, GlobalMaxPooling1D, Conv1D
from keras.preprocessing import text, sequence
from keras.callbacks import Callback
from keras.models import model_from_json


def get_reverse_mapping(data):
  result = list()
  _dict = ['Normal','Suggestion','Task Assigned']
  for y in data:
    result.append(_dict.index(y))
  return np.array(result)
  
def get_mapping(data):
  result = list()
  _dict = ['Normal','Suggestion','Task Assigned']
  for y in data:
    result.append(_dict[y])
  return np.array(result)
  
def get_max(data):
  result = list()
  for _data in data:
    result.append(np.argmax(_data))
  return np.array(result)

def get_classification_results (sentences):
  maxlen = 600
  max_features = 11760

  test_sentence = sentences
  test_corpus = pd.DataFrame(test_sentence)

  pos_tags_test = test_corpus[0].apply(lambda x : " ".join(item[1] for item in pos_tag(word_tokenize(x)))).values
  test_corpus = test_corpus[0].values + " " + pos_tags_test

  tokenizer = text.Tokenizer(num_words = max_features)
  tokenizer.fit_on_texts(list(test_corpus))

  test_corpus = tokenizer.texts_to_sequences(test_corpus)

  test_corpus = sequence.pad_sequences(test_corpus, maxlen = maxlen)
  return get_mapping(get_max(loaded_model.predict(test_corpus, batch_size = 128, verbose = 1)))

def get_all_sentences(sentences):
    all_word = []
    for text in sentences:
        all_word.append(text['sentence'])
    return all_word


if __name__ == '__main__':
  # load json and create model
  json_file = open('model.json', 'r')
  loaded_model_json = json_file.read()
  json_file.close()
  loaded_model = model_from_json(loaded_model_json)
  # load weights into new model
  loaded_model.load_weights("model.h5")
  print("Loaded model from disk")

  # evaluate loaded model on test data
  loaded_model.compile(loss = 'categorical_crossentropy', optimizer = 'adam', metrics = ['accuracy'])

  sentences = ['Hi']
  with open('/content/data_meeting_text1.txt') as sentences_file:
    sentences_json = json.load(sentences_file)
    sentences = get_all_sentences(sentences_json['structured_meeting_texts_without_introduction'])
    classification = get_classification_results(sentences)
    df = pd.DataFrame({'sentence': sentences, 'result': classification}, columns=['sentence', 'result'])