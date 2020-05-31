import json
import os
import glob
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import en_core_web_sm
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm
from sklearn.decomposition import PCA
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.cluster import Birch
from sklearn.cluster import AgglomerativeClustering
from sklearn.mixture import GaussianMixture
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix
from sklearn.linear_model import SGDClassifier
import itertools
import pickle
import tensorflow as tf

tf.compat.v1.enable_eager_execution()
import tensorflow_hub as hub


def get_file_content(filename: str) -> json:
    with open(filename) as file_data:
        _data = json.load(file_data)

    return _data


def selected_topics(model, vectorizer, top_n=5):
    current_words = []
    keywords = []

    for idx, topic in enumerate(model.components_):
        words = [(vectorizer.get_feature_names()[i], topic[i]) for i in topic.argsort()[:-top_n - 1:-1]]
        for word in words:
            if word[0] not in current_words:
                keywords.append(word)
                current_words.append(word[0])

    keywords.sort(key=lambda x: x[1])
    keywords.reverse()
    return_values = []
    for ii in keywords:
        return_values.append(ii[0])
    return return_values


def spacy_tokenizer(sentence):
    mytokens = parser(sentence)
    mytokens = [word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in mytokens]
    mytokens = [word for word in mytokens if word not in stopwords and word not in punctuations]
    mytokens = " ".join([i for i in mytokens])
    return mytokens


if __name__ == '__main__':
    k = 4
    NUM_TOPICS_PER_CLUSTER = 20
    file = "data_meeting_text_pdf_meetingtranscript566.txt"

    punctuations = string.punctuation
    stopwords = list(STOP_WORDS)
    custom_stop_words = [
        'doi', 'preprint', 'copyright', 'peer', 'reviewed', 'org', 'https', 'et', 'al', 'author', 'figure',
        'rights', 'reserved', 'permission', 'used', 'using', 'biorxiv', 'medrxiv', 'license', 'fig', 'fig.',
        'al.', 'Elsevier', 'PMC', 'CZI', 'www'
    ]
    stopwords = list(set(stopwords) | set(custom_stop_words))
    parser = spacy.load('en_core_web_sm', disable=['ner', 'tagger'])
    parser.max_length = 7000000
    embed = hub.load("D:\\Embeddings\\universal-sentence-encoder_4")

    data = get_file_content(file)
    df = json_normalize(data, sep="_")

    df["processed_text"] = df["sentence"].apply(spacy_tokenizer)

    text = df['processed_text'].values
    A = embed(text)
    pca = PCA(n_components=0.95, random_state=42)
    A_reduced = pca.fit_transform(A.numpy())

    agglomerativeClustering = AgglomerativeClustering(n_clusters=k, affinity='euclidean', linkage='ward')
    y_pred_agglomerativeClustering = agglomerativeClustering.fit_predict(A_reduced)
    df['cluster'] = y_pred_agglomerativeClustering

    with open('clusters.txt', 'w') as file:
        json.dump(df.to_json(), file)

    vectorizers = []

    for ii in range(0, k):
        # Creating a vectorizer
        vectorizers.append(CountVectorizer(min_df=5, max_df=0.9, stop_words='english', lowercase=True,
                                           token_pattern='[a-zA-Z\-][a-zA-Z\-]{2,}'))

    vectorized_data = []
    for current_cluster, cvec in enumerate(vectorizers):
        try:
            vectorized_data.append(cvec.fit_transform(df.loc[df['cluster'] == current_cluster, 'processed_text']))
        except Exception as e:
            vectorized_data.append(None)


    lda_models = []
    for ii in range(0, k):
        # Latent Dirichlet Allocation Model
        lda = LatentDirichletAllocation(n_components=NUM_TOPICS_PER_CLUSTER, max_iter=10, learning_method='online',
                                        verbose=False, random_state=42)
        lda_models.append(lda)

    clusters_lda_data = []

    for current_cluster, lda in enumerate(lda_models):
        if vectorized_data[current_cluster] is not None:
            clusters_lda_data.append((lda.fit_transform(vectorized_data[current_cluster])))

    keywords = {}
    for current_vectorizer, lda in enumerate(lda_models):
        if vectorized_data[current_vectorizer] is not None:
            keywords[current_vectorizer + 1] = selected_topics(lda, vectorizers[current_vectorizer])

    with open('clusters_words.txt', 'w') as output_file:
        json.dump(keywords, output_file)