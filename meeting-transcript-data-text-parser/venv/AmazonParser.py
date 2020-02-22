import json
from nltk.tokenize import TweetTokenizer, word_tokenize, sent_tokenize
import csv
import pandas as pd
import codecs

folder_path = 'D:\MinutesOfMeeting\meeting-audio-data'
file_name = '2. Amazon.json'


def parse_amazon_transcribe_file(data):
    resultant = list()
    segments = [d['alternatives'][0]['transcript'] for d in data['results']['segments']]
    speaker_labels = [d['speaker_label'] for d in data['results']['speaker_labels']['segments']]

    dialogue_id = 0

    aggregated_segments = list()
    aggregated_speakers = list()
    for i, segment in enumerate(segments):
        if i > 0 and aggregated_speakers[-1] == speaker_labels[i]:
            aggregated_segments[-1] += ' ' + segment
        else:
            aggregated_speakers.append(speaker_labels[i])
            aggregated_segments.append(segment)

    for i, segment in enumerate(aggregated_segments):
        sentences = sent_tokenize(segment)
        for ind, sentence in enumerate(sentences):
            if sentence == '':
                break
            res = dict()
            res['sentence'] = sentence.strip()
            res['speaker'] = aggregated_speakers[i]
            res['dialogue_id'] = dialogue_id
            resultant.append(res)
            dialogue_id += 1
    return resultant


if __name__ == '__main__':

    _data = json.load(codecs.open(folder_path + '\\' + file_name, 'r', 'utf-8-sig'))
    final = parse_amazon_transcribe_file(_data)
    with open('data_meeting_text_amazon.txt', 'w') as output_file:
        json.dump(final, output_file)
    with open('data_meeting_text_amazon.csv', 'w') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(['sentence', 'speaker', 'dialogue_id'])
        for data in final:
            writer.writerow([data['sentence'],
                             data['speaker'],
                             data['dialogue_id']])
