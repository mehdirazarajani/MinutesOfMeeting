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


def _remove_stopwords(sen):
    sen_new = " ".join([i for i in sen if i not in stop_words])
    return sen_new


def _create_dictionary_table(sentences) -> dict:
    frequency_table = dict()
    stop_words = set(stopwords.words("english"))
    for text_string in sentences:
        words = word_tokenize(text_string)
        stem = PorterStemmer()
        for wd in words:
            wd = stem.stem(wd)
            if wd in stop_words:
                continue
            if wd in frequency_table:
                frequency_table[wd] += 1
            else:
                frequency_table[wd] = 1
    return frequency_table


def _calculate_sentence_scores(sentences, frequency_table) -> dict:
    sentence_weight = dict()
    for sentence in sentences:
        sentence_wordcount = (len(word_tokenize(sentence)))
        sentence_wordcount_without_stop_words = 0
        for word_weight in frequency_table:
            if word_weight in sentence.lower():
                sentence_wordcount_without_stop_words += 1
                # sentence_hash = hashlib.md5(sentence.encode())
                sentence_hash = sentence
                if sentence_hash in sentence_weight:
                    sentence_weight[sentence_hash] += frequency_table[word_weight]
                else:
                    sentence_weight[sentence_hash] = frequency_table[word_weight]
        sentence_weight[sentence_hash] = (sentence_weight[sentence_hash] + 0.5) / (
                    sentence_wordcount_without_stop_words + 1)

    return sentence_weight


def _calculate_average_score(sentence_weight) -> int:
    sum_values = 0
    for entry in sentence_weight:
        sum_values += sentence_weight[entry]
    average_score = (sum_values / len(sentence_weight))
    return average_score


def _get_article_summary(sentences, sentence_weight, threshold):
    sentence_counter = 0
    article_summary = ''

    for sentence in sentences:
        # sentence_hash = hashlib.md5(sentence.encode())
        sentence_hash = sentence
        if sentence_hash in sentence_weight and sentence_weight[sentence_hash] >= (threshold):
            article_summary += " " + sentence
            sentence_counter += 1
    return article_summary


def sorted_weighted_frequency_sentences(sentences):
    # creating a dictionary for the word frequency table
    frequency_table = _create_dictionary_table(sentences)

    # algorithm for scoring a sentence by its words
    sentence_scores = _calculate_sentence_scores(sentences, frequency_table)
    sorted_sentence_scores = sorted([(key, value) for (key, value) in sentence_scores.items()], key=lambda x: x[1],reverse=False)

    # getting the threshold
    threshold = _calculate_average_score(sentence_scores)

    # #producing the summary
    meeting_summary = _get_article_summary(sentences, sentence_scores, 1.5 * threshold)

    return sorted_sentence_scores, meeting_summary


if __name__ == '__main__':

    with open('data_meeting_text_amazon.txt') as data_file:
        _data = json.load(data_file)
        sentences = [d['sentence'].lower() for d in _data]
        speakers = [d['speaker'] for d in _data]

    stop_words = stopwords.words('english')
    clean_sentences = [_remove_stopwords(r.split()) for r in sentences]

    sentence_ranking, summary = sorted_weighted_frequency_sentences(sentences)

    with open('ranked_sentences_frequency_based.csv', 'w') as output_file:
        writer = csv.writer(output_file)
        for sen in sentence_ranking:
            writer.writerow(list(sen))

    with open('summary_frequency_based.txt', 'w') as output_file:
        output_file.write(summary)