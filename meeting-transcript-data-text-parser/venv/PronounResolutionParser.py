import json
import re

folder_path = 'D:\\MinutesOfMeeting\\meeting-transcript-data-text-parser\\venv'
file_name = 'pronoun resolution output data.txt'
sentence_regex = re.compile(r'''^([\w\s\.]+) said "(.*)"$''')


def parse_pronoun_resolution_transcribe_file(data):
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

    with open(folder_path + '\\' + file_name) as data_file:
        _data = data_file.readlines()
        final = parse_pronoun_resolution_transcribe_file(_data)
        with open('data_meeting_text_pronoun.txt', 'w') as output_file:
            json.dump(final, output_file)