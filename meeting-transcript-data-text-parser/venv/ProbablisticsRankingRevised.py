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


def fill_cluster_collection(cluster_corpus):
    resultants = dict()
    raw_clusters = list()

    sp = spacy.load('en_core_web_sm')

    for ind, cluster_text in enumerate(cluster_corpus):
        raw_clusters.append(cluster_text)
        resultants[str(ind)] = dict()
        resultant = dict()
        sentence = remove_stopwords(remove_punctuation(cluster_text.lower()))
        sentence = lemmatization(sentence, sp)
        # sentence = stemming(sentence)
        if ' ' in sentence:
            for word in sentence.split(' '):
                if word != '':
                    if word in resultant:
                        resultant[word] += 1
                    else:
                        resultant[word] = 1
        else:
            word = sentence
            if word != '':
                if word != '':
                    if word in resultant:
                        resultant[word] += 1
                    else:
                        resultant[word] = 1
        resultants[str(ind)] = resultant
    return raw_clusters, resultants


def calculate_prp(words_collection, cluster_collection, raw_clusters, raw_sentences):
    resulants = dict()

    for sentence in raw_sentences:
        resulants[sentence] = dict()

    n = len(raw_clusters)
    for ind in cluster_collection.keys():
        print()
        resulant = calculate_prp_for_cluster(words_collection, raw_sentences, ind, raw_clusters[int(ind)], cluster_collection, raw_sentences, n)
        for key_sentence, value_dict in resulant.items():
            for _k, _v in value_dict.items():
                cluster_name = raw_clusters[int(_k)]
                resulants[key_sentence][cluster_name] = _v
    return resulants


def calculate_prp_for_cluster(words_collection, sentences, cluster_name, cluster_value, cluster_collection, raw_sentences, n):
    pt_ut_dict = dict()
    r_set = calculate_r(cluster_value, sentences)

    sp = spacy.load('en_core_web_sm')

    for sentence in sentences:
        sentence = remove_stopwords(remove_punctuation(sentence.lower()))
        sentence = lemmatization(sentence, sp)

        if ' ' in sentence:
            for word in sentence.split(' '):
                if word not in words_collection:
                    pt, ut = 0, 0
                    pt_ut_dict[word] = (pt, ut)
                elif word not in pt_ut_dict:
                    pt, ut = calculate_pt_ut_for_word(word, words_collection[word], r_set, n)
                    pt_ut_dict[word] = (pt, ut)
        elif sentence not in words_collection:
            pt, ut = 0, 0
            pt_ut_dict[sentence] = (pt, ut)
        elif sentence not in pt_ut_dict:
            word = sentence
            pt, ut = calculate_pt_ut_for_word(word, words_collection[word], r_set, n)
            pt_ut_dict[word] = (pt, ut)

    resultants = dict()
    any_word_occured = False
    for ind, sentence in enumerate(sentences):
        sentence = remove_stopwords(remove_punctuation(sentence.lower()))
        sentence = lemmatization(sentence, sp)
        prob = 1.0
        if ' ' in sentence:
            for word in sentence.split(' '):
                if word not in pt_ut_dict:
                    continue
                pt, ut = pt_ut_dict[word]
                if pt == 0 and ut == 0:
                    continue
                else:
                    prob *= (pt / ut)
                any_word_occured = True
            if not any_word_occured:
                prob = 0
        elif sentence not in pt_ut_dict:
            prob = 0
        else:
            pt, ut = pt_ut_dict[sentence]
            if pt == 0 and ut == 0:
                prob = 0
            else:
                prob *= (pt / ut)
        resultants[raw_sentences[ind]] = {cluster_name:prob}
    return resultants


# return {word:(pt, ut)} -  not used currently
def _calculate_prp_for_cluster_for_sentence(sentence, word_collection, cluster_collection, r, n):
    resultants = dict()
    if ' ' in sentence:
        for word in sentence.split(' '):
            pt, ut = calculate_pt_ut_for_word(word, word_collection[word], cluster_collection, r, n)
            resultants[word] = (pt, ut)
    else:
        word = sentence
        pt, ut = calculate_pt_ut_for_word(word, word_collection[word], cluster_collection, r, n)
        resultants[word] = (pt, ut)
    return resultants


# calculate pt, ut as tuple
def calculate_pt_ut_for_word(word, word_collection, r_set, n):
    rt = 0
    r = len(r_set)

    for value in r_set:
        if word in value:
            rt += 1

    nt = word_collection['cluster_count']

    pt = (rt + 0.5) / (r + 1.0)
    ut = (nt - rt + 0.5) / (n - r + 1.0)
    return pt, ut


# return set of sentences that are relevant to cluster
def calculate_r(cluster_words, sentences):

    sp = spacy.load('en_core_web_sm')

    contain_cluster_word = set()

    if ' ' in cluster_words:
        cluster_words_set = set(cluster_words.split(' '))
    else:
        cluster_words_set = {cluster_words}

    for sentence in sentences:

        sentence = remove_stopwords(remove_punctuation(sentence.lower()))
        sentence = lemmatization(sentence, sp)

        if ' ' in sentences:
            for word in sentence:
                if word in cluster_words_set:
                    contain_cluster_word.add(sentence)
                    break
        else:
            if sentence in cluster_words_set:
                contain_cluster_word.add(sentence)
    return contain_cluster_word


def find_the_max_ranked_cluster(title, clusters, raw_sentences, prp):
    resultants = dict()
    index = 0
    for cluster in clusters:
        resultants[cluster] = []
    for text, scores in prp.items():
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
        raw_clusters, cluster_collection = fill_cluster_collection(cluster_corpus)
    with open('data_meeting_text1.txt') as text_file:
        meeting_text = json.load(text_file)
        all_words_in_collection, collections = fill_the_collection(cluster_corpus, meeting_text[
            'structured_meeting_texts_without_introduction'])
        all_sentences = get_all_sentences(meeting_text['structured_meeting_texts_without_introduction'])

    with open('sentences.txt','w') as file:
        for line in all_sentences:
            file.write(line + '\n')

    with open('collections.txt', 'w') as outfile1:
        json.dump(collections, outfile1)
    all_prp = calculate_prp(collections, cluster_collection, raw_clusters, all_sentences)

    with open('prp.txt', 'w') as outfile1:
        json.dump(all_prp, outfile1)
        # write_csv_pir(all_pir, cluster_corpus, all_sentences, 'result pir.csv')
    clustered_sentences = find_the_max_ranked_cluster('clustered_sentences', cluster_corpus, meeting_text[
        'structured_meeting_texts_without_introduction'], all_prp)
    with open('clustered_sentences_revisied.txt', 'w') as outfile1:
        json.dump(clustered_sentences, outfile1)
