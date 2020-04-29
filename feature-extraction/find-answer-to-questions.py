import datetime
import re
import json

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

from Trie import TrieNode, find_a_word
from sutimeParser import detectWhenAnswer

# synonyms of yes and acceptance
# affirmative amen fine good okay ok true yea alright aye certainly definitely exactly gladly granted indubitably naturally positively precisely surething surely undoubtedly unquestionably willingly yep
# stemmed results of the above words
# affirm amen fine good okay ok true yea alright aye certainli definit even so exactli gladli grant indubit natur posit precis sure thing sure undoubtedli unquestion willingli yep
yes_synm_stem_regex = re.compile(
    r'(affirm|amen|fine|good|okay|ok|true|yea|alright|aye|certainli|definit|even|so|exactli|gladli|grant|indubit|natur|posit|precis|sure|thing|sure|undoubtedli|unquestion|willingli|yep)[\W]*')

# synonyms of no and negation
# antithesis antonym blank cancellation contrary converse counterpart disavowal disclaimer forget gainsaying inverse negatory negative neutralization nix no nonexistence nothingness nullification nullity opposite opposition proscription refusal rejection renunciation repudiation reverse vacuity veto void
# stemmed results of the above words
# antithesi antonym blank cancel contrari convers counterpart disavow disclaim forget it gainsay invers negatori neg neutral nix no nonexist nothing nullif nulliti opposit opposit proscript refus reject renunci repudi revers vacuiti veto void

no_synm_stem_regex = re.compile(
    r'(antithesis|antonym|blank|cancellation|contrary|converse|counterpart|disavowal|disclaimer|forget|gainsaying|inverse|negatory|negative|neutralization|nix|no|nonexistence|nothingness|nullification|nullity|opposite|opposition|proscription|refusal|rejection|renunciation|repudiation|reverse|vacuity|veto|void)[\W]*')

stemmer = PorterStemmer()

all_names_trie_root: TrieNode = TrieNode('*')
max_mismatch_allowed = 4
attendees_names = []


def answer_detection(question_sentence, adjacent_sentences, max_grid=20):
    i = 0

    possible_answers = []

    _adjacent_sentences = []

    for adjacent_sentence in adjacent_sentences:

        answer = (False, "")

        if question_sentence['speaker'] != adjacent_sentence['speaker']:
            i += 1
            _adjacent_sentences.append(adjacent_sentence)
        # not consider the text of the same person
        else:
            continue
        # when next question occures stop search for the answer
        if adjacent_sentence['sentence-type'] == 'Interrogative':
            break
        # iterate until the max length is not reached
        if i < max_grid:
            break

    for adjacent_sentence in _adjacent_sentences:
        if question_sentence['question-type'] == "affirmation":
            answer = detect_affirmative(question_sentence['sentence'], adjacent_sentence['sentence'])
        # elif question_sentence['question-type'] == "what":
        #     answer = dete(question_sentence, adjacent_sentence)
        elif question_sentence['question-type'] == "when":
            answer = detect_when(question_sentence['sentence'], adjacent_sentence['sentence'])
        elif question_sentence['question-type'] == "who":
            answer = detect_who(question_sentence['sentence'], adjacent_sentence['sentence'])

        if answer[0]:
            possible_answers.append(answer[1])

    if len(possible_answers) == 0:
        return False, ""

    return True, possible_answers


def detect_affirmative(question, adjacent):
    adjacent_text_tokens = word_tokenize(adjacent)
    adjacent_text_tokens_sw = {stemmer.stem(word) for word in adjacent_text_tokens if word not in stopwords.words()}

    if len(adjacent_text_tokens_sw) < max_mismatch_allowed + 1:
        for word in adjacent_text_tokens_sw:
            if yes_synm_stem_regex.match(word):
                return True, "YES"
            if no_synm_stem_regex.match(word):
                return True, "NO"
    elif len(adjacent_text_tokens_sw) == 0:
        for word in adjacent_text_tokens:
            word = stemmer.stem(word)
            if yes_synm_stem_regex.match(word):
                return True, "YES"
            if no_synm_stem_regex.match(word):
                return True, "NO"
    else:
        question_text_tokens = word_tokenize(question)
        question_text_tokens_sw = {stemmer.stem(word) for word in question_text_tokens if word not in stopwords.words()}
        if len(question_text_tokens_sw.intersection(adjacent_text_tokens_sw)) >= (
                len(question_text_tokens_sw) - max_mismatch_allowed):
            for word in adjacent_text_tokens_sw:
                if yes_synm_stem_regex.match(word):
                    return True, "YES"
                if no_synm_stem_regex.match(word):
                    return True, "NO"
    return False, ""


def detect_who(question, adjacent):
    adjacent_text_tokens = word_tokenize(adjacent)
    adjacent_text_tokens_sw = {word for word in adjacent_text_tokens if word not in stopwords.words()}

    for attendees_name in attendees_names:
        if attendees_name.lower() in adjacent:
            return True, attendees_name.title()

    if len(adjacent_text_tokens_sw) < max_mismatch_allowed + 1:
        name = ''
        for word in adjacent_text_tokens_sw:
            if find_a_word(all_names_trie_root, word):
                name += " " + word.title()
            else:
                name = ''
        if name != '':
            return True, name.strip()
    else:
        question_text_tokens = word_tokenize(question)
        question_text_tokens_sw = {stemmer.stem(word) for word in question_text_tokens if word not in stopwords.words()}
        adjacent_text_tokens_sw_stem = {stemmer.stem(word) for word in adjacent_text_tokens_sw}

        if len(question_text_tokens_sw.intersection(adjacent_text_tokens_sw_stem)) >= (
                len(question_text_tokens_sw) - max_mismatch_allowed):
            name = ''
            for word in adjacent_text_tokens_sw:
                if find_a_word(all_names_trie_root, word):
                    name += " " + word.title()
                else:
                    name = ''
            if name != '':
                return True, name.strip()
    return False, ""


def detect_when(question, adjacent):
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')

    for line in adjacent:
        resultant = detectWhenAnswer(date_str, line)
        if resultant[0]:
            return resultant

    return False, ""


def getAdjacentSentences(allQuestions, curIndex):
    count = len(allQuestions)
    startingIndex = min(count - 1, curIndex + 1)
    return allQuestions[startingIndex:]


def getPossibleAnswerForAllQuestions(allData):
    resultants = []
    for i, data in enumerate(allData):
        if data['sentence-type'] == 'Interrogative':
            resultant = {'question': data['sentence'], 'dialogue_id': data['dialogue_id'],
                         'question-type': data['question-type']}
            adjacent = getAdjacentSentences(allData, i)
            res = answer_detection(data, adjacent)

            if res[0]:
                resultant['is-result-found'] = True
                resultant['result'] = res[1]
            else:
                resultant['is-result-found'] = False
            resultants.append(resultant)
    return resultants


if __name__ == '__main__':
    with open("features-extracted.txt", 'r') as input_file:
        sentences = json.load(input_file)

    with open('questions-answers.txt', 'w') as output_file:
        json.dump(getPossibleAnswerForAllQuestions(sentences), output_file)
