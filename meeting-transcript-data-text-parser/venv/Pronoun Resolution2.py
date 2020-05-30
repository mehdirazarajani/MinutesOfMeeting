import json
import re
import csv

from pycorenlp import StanfordCoreNLP

nlp = StanfordCoreNLP('http://localhost:9000')

folder_path = 'D:\\MinutesOfMeeting\\meeting-transcript-data\\meetingTranscripts.txt(good)'
file_name = 'data_meeting_text_pdf.txt'
sentence_regex = re.compile(r'''^([\w\s\._]+) said "(.*)$''')


def is_pronoun(possible_pronoun):
    return possible_pronoun in ["he", "him", "his",
                                "she", "her", "hers",
                                "it", "its",
                                "they", "them", "their", "theirs",
                                "we", "us", "our"
                                ]


def is_possessive(pronoun, pronoun_coref, sentences):
    sentence_index = pronoun_coref[1]
    word_index = pronoun_coref[3]
    sentence = sentences[sentence_index]
    # print sentence
    words = sentence["words"]
    # print words
    word = words[word_index]
    # print word
    pos = word[1]["PartOfSpeech"]
    # print pos
    if pronoun == "her":
        # print words
        # print pronoun_index
        # print words[pronoun_index]
        # print words[pronoun_index][1]
        # print words[pronoun_index][1]["PartOfSpeech"]
        # return pos == "PRP$"
        return False
    else:
        return pronoun in ["his", "hers", "its", "their", "theirs", "our"]


def sent_length(sentence):
    no_quote_sentence = re.sub("'", " '", sentence)
    return len(no_quote_sentence.split(" "))


def sent_replace(sentence, index, replacement):
    no_quote_sentence = re.sub("'", " ", sentence)
    new_sentence = no_quote_sentence.split(" ")
    new_sentence[index] = replacement
    return " ".join(new_sentence)


def clean(word):
    w = re.sub(" 's$", "", word)
    w = re.sub("'s$", "", w)
    return w


def resolve(corenlp_output):
    """ Transfer the word form of the antecedent to its associated pronominal anaphor(s) """
    for coref in corenlp_output['corefs']:
        mentions = corenlp_output['corefs'][coref]
        antecedent = mentions[0]  # the antecedent is the first mention in the coreference chain
        for j in range(1, len(mentions)):
            mention = mentions[j]
            if mention['type'] == 'PRONOMINAL':
                # get the attributes of the target mention in the corresponding sentence
                target_sentence = mention['sentNum']
                target_token = mention['startIndex'] - 1
                # transfer the antecedent's word form to the appropriate token in the sentence
                corenlp_output['sentences'][target_sentence - 1]['tokens'][target_token]['word'] = antecedent['text']


def print_resolved(corenlp_output):
    """ Print the "resolved" output """
    possessives = ['hers', 'his', 'their', 'theirs']
    for sentence in corenlp_output['sentences']:
        for token in sentence['tokens']:
            output_word = token['word']
            # check lemmas as well as tags for possessive pronouns in case of tagging errors
            if token['lemma'] in possessives or token['pos'] == 'PRP$':
                output_word += "'s"  # add the possessive morpheme
            output_word += token['after']
            print(output_word, end='')


def get_str_resolved(corenlp_output):
    resolved = ""
    possessives = ['hers', 'his', 'their', 'theirs']
    for sentence in corenlp_output['sentences']:
        for token in sentence['tokens']:
            output_word = token['word']
            # check lemmas as well as tags for possessive pronouns in case of tagging errors
            if token['lemma'] in possessives or token['pos'] == 'PRP$':
                output_word += "'s"  # add the possessive morpheme
            output_word += token['after']
            resolved += output_word
    return resolved


def parse_pronoun_resolution_transcribe_data(data):
    resultant = list()
    dialogue_id = 0
    for i in data:
        matcher = re.match(sentence_regex, i)
        if matcher is None:
            continue
        speaker_label = matcher.groups()[0]
        segment = matcher.groups()[1]
        if '.' != segment[-1]:
            segment += '.'
        for sentence in segment.split('.'):
            if sentence == '':
                break
            res = dict()
            res['sentence'] = sentence.strip() + '.'
            res['speaker'] = speaker_label
            res['dialogue_id'] = dialogue_id
            resultant.append(res)
        dialogue_id += 1
    return resultant


if __name__ == '__main__':

    # goto stanfordcofenlp folder
    # run java -mx6g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -annotators "tokenize,ssplit,pos,lemma,parse,sentiment" -port 9000 -timeout 30000

    # text = "Tom and Jane are good friends. They are cool. He knows a lot of things and so does she. His car is red, but " \
    #        "hers is blue. It is older than hers. The big cat ate its dinner."

    with open('data_meeting_text_amazon_2.txt') as input_file:
        input_data = json.load(input_file)
        text_arr = [cur_data['speaker'].replace(':', '') + ''' said "''' + cur_data['sentence'].replace('''"''', '') for cur_data in input_data]
        outputs = []

        for text in text_arr:
            output = nlp.annotate(text,
                                  properties={'annotators': 'dcoref', 'outputFormat': 'json', 'ner.useSUTime': 'false'})
            resolve(output)
            print('Original:', text)
            print('Resolved: ', end='')
            print_resolved(output)
            outputs.append(get_str_resolved(output))

        outputs = [output.replace("``", '''"''').replace("""''""", '''"''') for output in outputs]

        final = parse_pronoun_resolution_transcribe_data(outputs)
        with open('data_meeting_text_pronoun.txt', 'w') as output_file:
            json.dump(final, output_file)
