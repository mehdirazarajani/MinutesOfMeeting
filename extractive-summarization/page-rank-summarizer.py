import numpy as np
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import re
import json
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
import hashlib
import csv

folder_path = 'D:\MinutesOfMeeting\meeting-transcript-data-text-parser\\venv'
# file_name = 'data_meeting_text_amazon.txt'
file_name = 'data_meeting_text_pdf.txt'


def _remove_stopwords(sen):
    sen_new = " ".join([i for i in sen if i not in stop_words])
    return sen_new


def _get_word_embeddings(model_name):
    word_embeddings = dict()
    f = open(model_name, encoding='utf-8')
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        word_embeddings[word] = coefs
    f.close()
    return word_embeddings


def _get_sentence_vectors(word_embeddings, sentences, dim):
    sentence_vectors = list()
    for i in clean_sentences:
        if len(i) != 0:
            v = sum([word_embeddings.get(w, np.zeros((dim,))) for w in i.split()]) / (len(i.split()) + 0.001)
        else:
            v = np.zeros((dim,))
        sentence_vectors.append(v)
    return sentence_vectors


def _get_similarity_matrix(size, sentence_vectors, dim):
    sim_mat = np.zeros([size, size])
    for i in range(size):
        for j in range(size):
            if i != j:
                sim_mat[i][j] = \
                    cosine_similarity(sentence_vectors[i].reshape(1, dim), sentence_vectors[j].reshape(1, dim))[0, 0]
    return sim_mat


def _get_network_graph_scores(sim_mat):
    nx_graph = nx.from_numpy_array(sim_mat)
    scores = nx.pagerank(nx_graph)
    return scores


def _get_sentence_ranking(sentences, ng_scores):
    ranked_sentences = sorted(((ng_scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    return ranked_sentences


def page_rank_algorithm(model_file, dim):
    word_embeddings = _get_word_embeddings(model_file)
    sentence_vectors = _get_sentence_vectors(word_embeddings, clean_sentences, dim)
    similarity_vector = _get_similarity_matrix(len(sentences), sentence_vectors, dim)
    network_graph_score = _get_network_graph_scores(similarity_vector)
    sentence_ranking = _get_sentence_ranking(sentences, network_graph_score)
    return sentence_ranking


if __name__ == '__main__':

    # nltk.download('stopwords')# one time execution
    # nltk.download('punkt') # one time execution

    with open(folder_path + '\\' + file_name) as data_file:
        _data = json.load(data_file)
        sentences = [d['sentence'].lower() for d in _data]
        speakers = [d['speaker'] for d in _data]

    stop_words = stopwords.words('english')
    clean_sentences = [_remove_stopwords(r.split()) for r in sentences]
    sentence_ranking = page_rank_algorithm('glove.6B.100d.txt', 100)

    with open('ranked_sentences_100d.csv', 'w') as output_file:
        writer = csv.writer(output_file)
        for sen in sentence_ranking:
            writer.writerow(list(sen))
