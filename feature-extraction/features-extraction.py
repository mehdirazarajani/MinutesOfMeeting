from nltk.corpus import words
import datefinder
import csv
import json
import re

import datefinder
from nltk.corpus import words
from nltk.tokenize import TweetTokenizer, word_tokenize, sent_tokenize
from pycorenlp import StanfordCoreNLP
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer


folder_path = 'D:\MinutesOfMeeting\sentence-classifier'
# file_name = 'data_meeting_text_amazon.txt'
file_name = 'classification.json'


def find_the_features(inp_sentences):
    _sentences_with_not = set()
    _sentences_with_date = set()
    _sentences_with_figure = set()
    _sentiment_with_score = list()
    tokenizer = TweetTokenizer()
    words_list = words.words()
    stopwords_list = set(stopwords.words('english'))

    for i, _sentence in enumerate(inp_sentences):
        tokens = tokenizer.tokenize(_sentence.lower())
        if is_not_word_included(words_list, tokens, stopwords_list):
            _sentences_with_not.add(i)
        if is_date_included(_sentence):
            _sentences_with_date.add(i)
        if is_figure_included(_sentence):
            _sentences_with_figure.add(i)
        _sentiment_with_score.append(get_sentiment(_sentence))

    return _sentences_with_not, _sentences_with_date, _sentences_with_figure, _sentiment_with_score


def is_not_word_included(words_list, tokens, stopwords):
    no_syns = {'no', 'not', 'nay', 'nix', 'never'}
    no_syns_rgx = r'^(no|not|nay|nix|never)$'
    # no_prefixes = {'in', 'un', 'non', 'de', 'dis', 'a', 'anti', 'im', 'il', 'ir', 'mis'}
    prefix_rgx = r'^(in|un|non|de|dis|anti|a|im|il|ir)\w+$'

    occs_of_not_synms = 0

    for i, token in enumerate(tokens):
        if re.search(no_syns_rgx, token):
            occs_of_not_synms += 1
        prefix = re.findall(prefix_rgx, token)
        if len(prefix) > 0:
            left_over = token[len(prefix[0]):]
            left_over_sentiment = get_sentiment(left_over)[0]
            original_sentiment = get_sentiment(token)[0]
            if left_over in words_list and original_sentiment == 'Negative' and left_over_sentiment == 'Positive' and i > 0:
                if _check_for_double_negation(tokens[:i], stopwords, no_syns):
                    occs_of_not_synms -= 1
                else:
                    return True
    return occs_of_not_synms > 0


def _check_for_double_negation(prev_tokens, stopwords, no_syns):
    for i in range(len(prev_tokens)-1,-1,-1):
        if prev_tokens[i] in stopwords:
            continue
        return prev_tokens[i] in no_syns
    return False


def is_date_included(inp_sentence):
    extracted_dates = datefinder.find_dates(inp_sentence)
    for extracted_date in extracted_dates:
        return True
    return False


def is_figure_included(tokens):
    number_words_rgx = r'^(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion|trillion)$'
    number_digit_rgx = r'[+-]?[0-9][0-9]*'
    for token in tokens:
        if re.search(number_words_rgx, token):
            return True
        if re.search(number_digit_rgx, token):
            return True
    return False


def get_sentiment(text):
    res = nlp.annotate(text,
                       properties={'annotators': 'sentiment',
                                   'outputFormat': 'json',
                                   'timeout': 900000,
                                   })
    if res == 'CoreNLP request timed out. Your document may be too long.':
        return 'Error', -1
    return res['sentences'][0]['sentiment'], res['sentences'][0]['sentimentValue']


if __name__ == '__main__':

    # import nltk
    # nltk.download('averaged_perceptron_tagger')

    # goto stanfordcofenlp folder
    # run java -mx6g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -annotators "tokenize,ssplit,pos,lemma,parse,sentiment" -port 9000 -timeout 30000

    nlp = StanfordCoreNLP('http://localhost:9000')

    with open(folder_path + '\\' + file_name) as data_file:
        _data = json.load(data_file)
        sentences = [d['sentence'].lower() for d in _data]
        speakers = [d['speaker'] for d in _data]
        dialogue_ids = [d['dialogue_id'] for d in _data]
        classification_types = [d['classification_type'] for d in _data]
        sentences_with_not, sentences_with_date, sentences_with_figure, sentiment_with_score = find_the_features(sentences)

        with open("features-extracted.csv", 'w') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(['dialogue_id', 'speaker', 'sentence', 'classification_type'
                             'not-word-found', 'date-found', 'figure (number) found', 'sentiment-type', 'sentiment-score'])
            for ind, sentence in enumerate(sentences):
                temp = list()
                temp.append(dialogue_ids[ind])
                temp.append(speakers[ind])
                temp.append(sentence)
                temp.append(classification_types[ind])
                temp.append(ind in sentences_with_not)
                temp.append(ind in sentences_with_date)
                temp.append(ind in sentences_with_figure)
                temp.append(sentiment_with_score[ind][0])
                temp.append(sentiment_with_score[ind][1])
                writer.writerow(temp)

        with open("features-extracted.txt", 'w') as output_file:
            resultants = []
            for ind, sentence in enumerate(sentences):
                resultant = {}
                resultant["dialogue_id"] = dialogue_ids[ind]
                resultant["speaker"] = speakers[ind]
                resultant["sentence"] = sentence
                resultant['classification_type'] = classification_types[ind]
                resultant["not-word-found"] = ind in sentences_with_not
                resultant["date-found"] = ind in sentences_with_date
                resultant["figure (number) found"] = ind in sentences_with_figure
                resultant["sentiment-type"] = sentiment_with_score[ind][0]
                resultant["sentiment-score"] = sentiment_with_score[ind][1]
                resultants.append(resultant)
            json.dump(resultants, output_file)
