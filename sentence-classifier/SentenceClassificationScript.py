from keras.models import model_from_json
from nltk.corpus import words
from nltk.tokenize import TweetTokenizer, word_tokenize, sent_tokenize
from pycorenlp import StanfordCoreNLP
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import SVC
import pickle
import pandas as pd
from nltk import pos_tag
from keras.preprocessing import text, sequence
import json
import numpy as np
import re


def get_mapping(data):
    result = list()
    _dict = ['Normal', 'Suggestion', 'Task Assigned']
    for y in data:
        result.append(_dict[y])
    return np.array(result)


def get_max(data):
    result = list()
    for _data in data:
        result.append(np.argmax(_data))
    return np.array(result)


def is_interrogative_sentence(_sentence, nlp, question_type_clf: SVC, vocab, classes):
    vectorizer = CountVectorizer(vocabulary=vocab, lowercase=True)

    is_question = False
    if '?' in _sentence:
        is_question = True
    else:
        output = nlp.annotate(_sentence, properties={'annotators': 'parse', 'outputFormat': 'json'})
        try:
            if ('SQ' or 'SBARQ') in output['sentences'][0]["parse"]:
                interrogative_sentences.add(i)
                is_question = True
        except:
            is_question = False
    if is_question:
        _sentence = _sentence.strip().lower()
        _sentence = re.sub('[^a-zA-z0-9\s\']', '', _sentence)
        sentence_vector = vectorizer.transform([_sentence])
        return True, "Interrogative" + '-' + classes[question_type_clf.predict(sentence_vector)[0]]
    else:
        return False, '-'


def get_classification_results(sentence, loaded_model):
    maxlen = 600
    max_features = 11760

    test_corpus = pd.DataFrame([sentence])

    pos_tags_test = test_corpus[0].apply(lambda x: " ".join(item[1] for item in pos_tag(word_tokenize(x)))).values
    test_corpus = test_corpus[0].values + " " + pos_tags_test

    tokenizer = text.Tokenizer(num_words=max_features)
    tokenizer.fit_on_texts(list(test_corpus))

    test_corpus = tokenizer.texts_to_sequences(test_corpus)

    test_corpus = sequence.pad_sequences(test_corpus, maxlen=maxlen)
    return get_mapping(get_max(loaded_model.predict(test_corpus, batch_size=128, verbose=1)))[0]


if __name__ == '__main__':
    # load json and create model
    json_file = open('model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("model.h5")
    print("Loaded model from disk")

    nlp = StanfordCoreNLP('http://localhost:9000')

    with open('question-type-classifier.bin', 'rb') as clf_file:
        question_type_clf = pickle.load(clf_file)

    with open('vocab.bin', 'rb') as clf_file:
        vocab = pickle.load(clf_file)

    with open('question-type-classes.bin', 'rb') as classes_file:
        questions_type_classes = pickle.load(classes_file)

    # evaluate loaded model on test data
    loaded_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    sentences = ['Hi']

    with open('data_meeting_text_pronoun.txt') as input_file:
        _data = json.load(input_file)
        sentences = [x['sentence'] for x in _data]

    resultants = []

    for i, sentence in enumerate(sentences):
        is_question, classification_type = is_interrogative_sentence(sentence, nlp, question_type_clf, vocab,
                                                                     questions_type_classes)

        if not is_question:
            classification_type = get_classification_results(sentence, loaded_model)

        resultant = _data[i]
        resultant['classification_type'] = classification_type
        resultants.append(resultant)

    with open('classification.json', 'w') as output_file:
        json.dump(resultants, output_file)
