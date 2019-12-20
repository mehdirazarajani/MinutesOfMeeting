import json
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

clusters = {
    '0': {'second', 'welcome', 'department', 'moved', 'opm', 'bucks', 'everyone', 'dod', 'carlos', 'act', 'steve',
          'navy', 'afge', 'fprac', 'year', 'two', 'good', 'us', 'defense', '129cid', 'really', 'j', 'used', 'nage',
          'thing'},
    '1': {'one', 'let', 'say', 'think', 'well', 'issue', 'county', 'permitted', 'know', 'road', 'kick', 'may', 'way',
          'would', 'lakes', 'geographic', 'announcements', 'fall', 'chips', 'couple', 'appreciate', 'settle', 'lake',
          'containing', 'employees'},
    '2': {'survey', 'well', 'like', 'issue', 'group', 'first', 'take', 'may', 'working', 'work', 'maybe', 'unless',
          'would', 'getting', 'people', 'seems', 'everybody', 'need', 'guess', 'issues', 'settle', 'business', 'really',
          'next', 'cases'},
    '3': {'questions', 'really', 'system', 'things', 'committee', 'variety', 'forms', 'seen', 'document', 'looked',
          'seeing', 'taking', 'entire', 'narrowly', 'individual', 'responsible', 'addressed', 'federal', 'raised',
          'rather', 'focus', 'different', 'sense', 'make', 'long'},
    '4': {'okay', 'oh', 'completely', 'separately', 'right', 'flat', 'fisher', 'fiscal', 'first', 'fingers', 'fine',
          'finding', 'figuring', 'yet', 'field', 'fenaughty', 'feel', 'federal', 'favor', 'faster', 'fall', 'facts',
          'fendt', 'flexibility', 'extension'},
    '5': {'dont', 'time', 'yet', 'think', 'got', 'need', 'know', 'issues', 'said', 'troubled', 'anyone', 'long',
          'reservoir', 'practice', 'understand', 'reporter', 'state', 'could', 'way', 'work', 'employees', 'else',
          'brought', 'anyhow', 'reason'},
    '6': {'thats', 'right', 'progress', 'yes', 'fine', 'big', 'paid', 'scratch', 'get', 'case', 'could', 'list', 'one',
          'forum', 'occur', 'meetings', 'month', 'issue', 'might', 'room', 'wanted', 'ask', 'dod', 'people',
          'committee'},
    '7': {'thank', 'putting', 'many', 'place', 'thoughts', 'chairman', 'like', 'one', 'would', 'yet', 'flat', 'fisher',
          'fiscal', 'first', 'fine', 'fingers', 'finding', 'figuring', 'field', 'fendt', 'fenaughty', 'feel', 'federal',
          'favor', 'faster'},
    '8': {'mark', 'want', 'respond', 'allen', 'agree', 'know', 'cover', 'fine', 'wouldnt', 'opm', 'issue', 'lost',
          'specific', 'would', 'work', 'group', 'get', 'faster', 'days', 'around', 'havent', 'seem', 'moving',
          'pleasure', 'discussing'},
    '9': {'discussion', 'question', 'last', 'time', 'group', 'would', 'late', 'bubbled', 'concerns', 'basis',
          'indicated', 'prepare', 'brings', 'year', 'ideas', 'memo', 'issues', 'could', 'less', 'philosophy', 'wrap',
          'survey', 'underlying', 'prevailing', 'try'},
    '10': {'look', 'take', 'lets', 'focus', 'would', 'previous', 'put', 'propose', 'none', 'hearing', 'agree', 'one',
           'group', 'needed', 'perhaps', 'approach', 'move', 'agenda', 'minutes', 'see', 'review', 'think', 'rule',
           'underlying', 'basically'},
    '11': {'wage', 'area', 'surveys', 'system', 'changes', 'committee', 'mississippi', 'northern', 'federal', 'dod',
           'schedules', 'making', 'issue', 'really', 'process', 'pay', 'addressed', 'operates', 'separate',
           'publication', 'stuff', 'beyond', 'already', 'submitted', 'corrections'},
    '12': {'yeah', 'whatever', 'ongoing', 'going', 'heart', 'come', 'maybe', 'actual', 'opinion', 'usual', 'work',
           'process', 'group', 'business', 'unless', 'different', 'issue', 'dod', 'survey', 'wage', 'fingers', 'frozen',
           'fine', 'finding', 'figuring'},
    '13': {'issue', 'last', 'consensus', 'meeting', 'review', 'minutes', 'item', 'brings', 'lee', 'otherwise', '1970s',
           'chairman', 'months', 'recommendation', 'able', 'us', 'county', 'ago', 'different', 'approved', 'new',
           'handling', 'objection', 'kind', 'three'},
    '14': {'go', 'going', 'everything', 'forward', 'mean', 'back', 'nobody', 'ahead', 'yes', 'raise', 'implemented',
           'nothing', 'dont', 'werent', 'member', 'fprac', 'occur', 'believe', 'information', 'pay', 'freeze',
           'additional', 'get', 'continue', 'well'},
    '15': {'anything', 'else', 'say', 'directors', 'memorandum', 'done', 'meant', 'foreclose', 'today', 'introduce',
           'heard', 'havent', 'anybody', 'longstanding', 'senator', 'boozman', 'issue', 'dont', 'raised', 'printers',
           'ink', 'engraved', 'except', 'worth', 'new'}
}


def remove_punctuation(text):
    '''a function for removing punctuation'''
    # replacing the punctuations with no space,
    # which in effect deletes the punctuation marks
    translator = str.maketrans('', '', string.punctuation)
    # return the text stripped of punctuation marks
    return text.translate(translator)


def remove_stopwords(text):
    '''a function for removing the stopword'''
    sw = stopwords.words('english')
    # extracting the stopwords from nltk library
    # removing the stop words and lowercasing the selected words
    text = [word.lower() for word in text.split() if word.lower() not in sw]
    # joining the list of words with space separator
    return " ".join(text)


if __name__ == '__main__':
    with open('data_meeting_text.txt') as train_file2:
        dict_train = json.load(train_file2)

    structured_meeting_texts = dict_train['structured_meeting_texts']
    sentences = []
    for i in structured_meeting_texts:
        sentences.append(i['sentence'])
    # Removing empty strings from list
    sentences = list(filter(None, sentences))
    raw_sentences = sentences[:]
    sentences = list(map(remove_punctuation, sentences))
    sentences = list(map(remove_stopwords, sentences))

    clustered_sentences = dict()
    for cluster in clusters.keys():
        clustered_sentences[cluster] = []

    for ind,sentence in enumerate(sentences):
        max_matching = 0
        max_matching_cluster = ''
        for key, words in clusters.items():
            matched = 0
            for word in words:
                if word in sentence:
                    matched += 1
            prob = matched / len(words)
            if prob > max_matching:
                max_matching = prob
                max_matching_cluster = key
        if not max_matching_cluster == '':
            clustered_sentences[max_matching_cluster].append(raw_sentences[ind])

    with open('clustered_sentences.txt', 'w') as outfile1:
        json.dump(clustered_sentences, outfile1)
