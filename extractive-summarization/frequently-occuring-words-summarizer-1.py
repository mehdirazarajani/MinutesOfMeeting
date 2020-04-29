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


def _create_dictionary_table(sentences) -> dict:
    frequency_table = dict()
    stop_words = set(stopwords.words("english"))
    stem = PorterStemmer()
    for text_string in sentences:
        words = word_tokenize(text_string)
        for wd in words:
            wd = stem.stem(wd)
            if wd in stop_words:
                continue
            if wd in frequency_table:
                frequency_table[wd] += 1
            else:
                frequency_table[wd] = 1
    return frequency_table


def _calculate_sentence_scores(sentences, frequency_dictionary) -> dict:
    _sentence_with_scores = dict()
    stem = PorterStemmer()
    stop_words = set(stopwords.words("english"))
    for text_string in sentences:
        score = 0
        number_of_non_stopwords = 0
        words = word_tokenize(text_string)
        for wd in words:
            wd = stem.stem(wd)
            if wd in stop_words:
                continue
            if re.match(r'^[A-Za-z0-9\s]+$',wd):
                number_of_non_stopwords += 1
                score += frequency_dictionary[wd]
        score = (score + 0.5) / (number_of_non_stopwords + 1)
        _sentence_with_scores[text_string] =  score
    return _sentence_with_scores


def _calculate_average_score(sentence_weight) -> int:
    sum_values = 0
    for entry in sentence_weight:
        sum_values += sentence_weight[entry]
    average_score = (sum_values / len(sentence_weight))
    return average_score


def _get_meeting_summary(sentences, sentence_weight, threshold):
    sentence_counter = 0
    meeting_summary = ''

    for sentence in sentences:
        # sentence_hash = hashlib.md5(sentence.encode())
        sentence_hash = sentence
        if sentence_hash in sentence_weight and sentence_weight[sentence_hash] >= (threshold):
            meeting_summary += " " + sentence
            sentence_counter += 1
    return meeting_summary


def sorted_weighted_frequency_sentences(sentences):
    # creating a dictionary for the word frequency table
    frequency_table = _create_dictionary_table(sentences)

    # algorithm for scoring a sentence by its words
    sentence_scores = _calculate_sentence_scores(sentences, frequency_table)
    sorted_sentence_scores = sorted([(key, value) for (key, value) in sentence_scores.items()], key=lambda x: x[1],reverse=False)

    # getting the threshold
    threshold = _calculate_average_score(sentence_scores)

    # #producing the summary
    meeting_summary = _get_meeting_summary(sentences, sentence_scores, 1.5 * threshold)

    return sorted_sentence_scores, meeting_summary


if __name__ == '__main__':

    with open(folder_path + '\\' + file_name) as data_file:
        _data = json.load(data_file)
        sentences = [d['sentence'].lower() for d in _data]
        speakers = [d['speaker'] for d in _data]

    stop_words = stopwords.words('english')

    sentence_ranking, summary = sorted_weighted_frequency_sentences(sentences)

    with open('ranked_sentences_frequency_based1.csv', 'w') as output_file:
        writer = csv.writer(output_file)
        for sen in sentence_ranking:
            writer.writerow(list(sen))

    with open('summary_frequency_based1.txt', 'w') as output_file:
        output_file.write(summary)
