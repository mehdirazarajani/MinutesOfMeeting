import json
import string
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import csv
import spacy
import operator
from jellyfish import jaro_distance



# clusters = [name of clusters]
# all_words_in_collection = set()
# collections = {word:{list:{cluster#:word_count},total_word_count:int,cluster_count:int}}


def remove_punctuation(text):
    """a function for removing punctuation"""
    # replacing the punctuations with no space,
    # which in effect deletes the punctuation marks
    translator = str.maketrans('', '', string.punctuation)
    # return the text stripped of punctuation marks
    return text.translate(translator)


def remove_stopwords(text):
    """a function for removing the stopword"""
    sw = stopwords.words('english')
    # extracting the stopwords from nltk library
    # removing the stop words and lowercasing the selected words
    text = [word.lower() for word in text.split() if word.lower() not in sw]
    # joining the list of words with space separator
    return " ".join(text)


def stemming(text):
    """a function which stems each word in the given text"""
    stemmer = PorterStemmer()
    text = [stemmer.stem(word) for word in text.split()]
    return " ".join(text)


def lemmatization(text, sp):
    """a function which lemmatization each word in the given text"""
    text = [word.lemma_ for word in sp(text)]
    return " ".join(text)


def __calculate_pir_for_word_for_cluster(word_details, total_cluster_count, cluster_name, sentence_len):
    try:
        rt = word_details['list'][cluster_name]
    except:
        rt = 0
    n = total_cluster_count

    r = word_details['total_word_count']
    nt = word_details['cluster_count']

    # r = sentence_len

    # nt = word_details['total_word_count']
    # r = word_details['cluster_count']

    pt = (rt + 0.5) / (r + 1.0)
    ut = (nt + 0.5) / (n + 1.0)
    return pt, ut


def __calculate_pir_for_sentence_for_cluster(sentence, cluster_collection, total_cluster_count, all_words,
                                             cluster_name):
    rsv = 1.0
    a_word_found = False
    if not ' ' in sentence:
        word = sentence
        if word in all_words:
            a_word_found = True
            pt, ut = __calculate_pir_for_word_for_cluster(cluster_collection[word], total_cluster_count,
                                                          cluster_name, len(sentence))
            rsv *= ((pt * (1 - ut)) / (ut * (1 - pt)))
        if not a_word_found:
            rsv = 0.0
    else:
        for word in sentence.split(' '):
            if word in all_words:
                a_word_found = True
                pt, ut = __calculate_pir_for_word_for_cluster(cluster_collection[word], total_cluster_count,
                                                              cluster_name, len(sentence))
                rsv *= ((pt * (1 - ut)) / (ut * (1 - pt)))
        if not a_word_found:
            rsv = 0.0
    return rsv


def calculate_pir_for_sentence(sentence, cluster_collection, total_cluster_count, all_words, clusters):
    resultant = dict()
    for ind, cluster in enumerate(clusters):
        resultant[cluster] = __calculate_pir_for_sentence_for_cluster(sentence, cluster_collection, total_cluster_count,
                                                                      all_words,
                                                                      str(ind))
    return resultant


def calculate_pir(text_corpus, cluster_collection, total_cluster_count, all_words, clusters):
    resultant = dict()
    for sentence in text_corpus:
        sentence = sentence['sentence']
        sentence = remove_stopwords(remove_punctuation(sentence.lower()))
        resultant[sentence] = calculate_pir_for_sentence(sentence, cluster_collection, total_cluster_count, all_words,
                                                         clusters)
    return resultant


def fill_the_collection(cluster_corpus, text_corpus):
    all_words_in_collection = set()
    # collections = {word:{list:{cluster#:word_count},total_word_count:int,cluster_count:int}}
    collections = dict()
    sp = spacy.load('en_core_web_sm')
    for sentence in text_corpus:
        sentence = sentence['sentence']
        sentence = remove_stopwords(remove_punctuation(sentence.lower()))
        sentence = lemmatization(sentence, sp)
        # sentence = stemming(sentence)
        if ' ' in sentence:
            for word in sentence.split(' '):
                if word != '':
                    all_words_in_collection.add(word)
                    collections = __update_collections(collections, cluster_corpus, word)
        else:
            word = sentence
            if word != '':
                all_words_in_collection.add(word)
                collections = __update_collections(collections, cluster_corpus, word)
    return all_words_in_collection, collections


def __update_collections(collections, cluster_corpus, word):
    list1 = dict()
    total_word_count = 0
    cluster_count = 0
    for ind, cluster in enumerate(cluster_corpus):
        if word in cluster:
            occ = cluster.count(word)
            list1[str(ind)] = occ
            total_word_count += occ
            cluster_count += 1
    collection = dict()
    collection['list'] = list1
    collection['total_word_count'] = total_word_count
    collection['cluster_count'] = cluster_count
    if total_word_count > 0:
        collections[word] = collection
    return collections


def write_csv_pir(pir, clusters, raw_sentences, filename):
    file = open(filename, 'w')
    writer = csv.writer(file)
    resultant = ['']
    index = 0
    for cluster in clusters:
        resultant.append(cluster)
    writer.writerow(resultant)
    for text, scores in pir.items():
        raw_sentence = raw_sentences[index]
        while not remove_stopwords(remove_punctuation(raw_sentence.lower())) == text:
            index += 1
            raw_sentence = raw_sentences[index]
        resultant = [raw_sentence]
        for score in scores.values():
            resultant.append(str(score))
        writer.writerow(resultant)
    file.close()


def fill_cluster_corpus(cluster_text):
    clusters = list()
    all_words_in_cluster = set()
    sp = spacy.load('en_core_web_sm')
    for key, values in cluster_text.items():
        for value in values:
            cluster = remove_stopwords(remove_punctuation(value['text'].lower()))
            cluster = lemmatization(cluster, sp)
            # cluster = stemming(cluster)
            all_words_in_cluster.update(cluster.split(' '))
            if cluster not in clusters:
                clusters.append(cluster)
    return all_words_in_cluster, clusters


def get_all_sentences(sentences):
    all_word = []
    for text in sentences:
        all_word.append(text['sentence'])
    return all_word


def find_the_max_ranked_cluster(title, clusters, raw_sentences, pir):
    resultants = dict()
    index = 0
    for cluster in clusters:
        resultants[cluster] = []
    for text, scores in pir.items():
        raw_sentence = raw_sentences[index]['sentence']
        sp = spacy.load('en_core_web_sm')
        while not lemmatization(remove_stopwords(remove_punctuation(raw_sentence.lower())), sp) == lemmatization(text,sp):
            index += 1
            raw_sentence = raw_sentences[index]['sentence']
            print('.')
        max_cluster = max(scores.items(), key=operator.itemgetter(1))[0]
        index += 1
        print(index)
        resultants[max_cluster].append(raw_sentences[index])
    return {title: resultants}


if __name__ == '__main__':
    with open('data_agenda1.txt') as agenda_file:
        cluster_text = json.load(agenda_file)
        all_words_in_cluster, cluster_corpus = fill_cluster_corpus(cluster_text['structured_agenda_texts'])
        print(all_words_in_cluster)
        print(cluster_corpus)
    with open('data_meeting_text1.txt') as text_file:
        meeting_text = json.load(text_file)
        all_words_in_collection, collections = fill_the_collection(cluster_corpus, meeting_text[
            'structured_meeting_texts_without_introduction'])
        all_sentences = get_all_sentences(meeting_text['structured_meeting_texts_without_introduction'])
        print(all_words_in_collection)
        print(len(all_words_in_collection))
        with open('collections.txt', 'w') as outfile1:
            json.dump(collections, outfile1)
        all_pir = calculate_pir(meeting_text['structured_meeting_texts_without_introduction'], collections,
                                len(cluster_corpus), all_words_in_cluster, cluster_corpus)
        with open('pir.txt', 'w') as outfile1:
            json.dump(all_pir, outfile1)
            # write_csv_pir(all_pir, cluster_corpus, all_sentences, 'result pir.csv')
        clustered_sentences = find_the_max_ranked_cluster('clustered_sentences', cluster_corpus, meeting_text[
            'structured_meeting_texts_without_introduction'], all_pir)
        with open('clustered_sentences.txt', 'w') as outfile1:
            json.dump(clustered_sentences, outfile1)