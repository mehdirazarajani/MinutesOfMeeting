import pickle
import re

import pandas as pd
from pycorenlp import StanfordCoreNLP
from sklearn import preprocessing
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC


class InterrogativeSentenceCheckerClassifier:

    @staticmethod
    def is_interrogative_sentence(sentence_to_be_checked, ind=0):
        if ind > 5:
            return False
        if '?' in sentence_to_be_checked:
            return True
        output = nlp.annotate(sentence_to_be_checked, properties={
            'annotators': 'parse',
            'outputFormat': 'json',
            'timeout': 1000,
        })
        if output == 'CoreNLP request timed out. Your document may be too long.':
            return sentence_to_be_checked.is_interrogative_sentence(sentence_to_be_checked, ind=ind + 1)
        if ('SQ' or 'SBARQ') in output['sentences'][0]["parse"]:
            return True
        return False

    def __init__(self):
        df = self.__get_data()
        df = self.__clean_data(df)
        df = self.__label_encode(df)
        vectorizer_classifier = self.__create_classifier(df)
        if vectorizer_classifier is not None:
            self.vectorizer = vectorizer_classifier['vectorizer']
            self.classifier = vectorizer_classifier['classifier']

    @staticmethod
    def __clean_data(df):
        df.rename(columns={0: 'text', 1: 'type'}, inplace=True)
        df['type'] = df['type'].str.strip()
        df['text'] = df['text'].apply(lambda x: x.lower())
        df['text'] = df['text'].apply((lambda x: re.sub('[^a-zA-z0-9\s\']', '', x)))
        return df[
            (df['type'] == 'what') | (df['type'] == 'who') | (df['type'] == 'when') | (df['type'] == 'unknown') | (
                    df['type'] == 'affirmation')]

    def __label_encode(self, df):
        self.le = preprocessing.LabelEncoder()
        self.le.fit(df['type'])
        df['label'] = list(self.le.transform(df['type']))
        return df

    @staticmethod
    def __create_classifier(df):
        v = CountVectorizer(analyzer='word', lowercase=True)
        X = v.fit_transform(df['text'])
        with open('vocab.bin', 'wb') as vocab_file:
            pickle.dump(v.vocabulary_, vocab_file)
        X_train, X_test, y_train, y_test = train_test_split(X, df['label'], test_size=0.3)
        clf_svm = SVC(kernel='linear')
        clf_svm.fit(X_train, y_train)
        preds = clf_svm.predict(X_test)
        print(classification_report(preds, y_test))
        print('Accuracy is: ', clf_svm.score(X_test, y_test))
        return {'vectorizer': v, 'classifier': clf_svm}

    @staticmethod
    def __get_data():
        return pd.read_csv('questions-classified.txt', sep='\t', header=None)

    def predict(self, sentence):
        ex = self.vectorizer.transform([sentence])
        return list(self.le.inverse_transform(self.classifier.predict(ex)))[0]


if __name__ == '__main__':
    # nltk.download('nps_chat')
    # nltk.download('punkt')
    #
    nlp = StanfordCoreNLP('http://localhost:9000')
    df = pd.read_csv('sentences-isquestions-dataset.csv')

    obj = InterrogativeSentenceCheckerClassifier()

    df_2 = df[df['is_question'] == 1].copy()
    df_2['question_type'] = df_2['QUERY'].apply(obj.predict)

    df_2['question_type'].value_counts()

    # with open('question-type-classifier.bin', 'wb') as file:
    #     pickle.dump(obj.classifier, file)

