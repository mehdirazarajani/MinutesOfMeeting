import json
from nltk.tokenize import TweetTokenizer, word_tokenize, sent_tokenize
import csv
import pandas as pd
import codecs

folder_path = 'D:\\MinutesOfMeeting\\meeting-transcript-data-text-parser\\venv'
file_name = '087980a1-0a61-46d0-a177-aa3a2d34010b.json'


def parse_amazon_transcribe_file(data):
    resultant = list()
    segments = [d for d in data['results']['items']]
    speaker_labels = get_speakers_labels(data['results']['speaker_labels']['segments'])

    dialogue_id = 0
    speaker_ind = 0
    last_speaker = 'spk_1'

    aggregated_segments = list()
    aggregated_speakers = list()
    for i, segment in enumerate(segments):
        speaker, speaker_ind = get_current_speaker(speaker_labels, speaker_ind, segment, last_speaker)
        last_speaker = speaker
        if i > 0 and aggregated_speakers[-1] == speaker:
            content = get_content_of_segment(segment)
            aggregated_segments[-1] += ' ' + content
        else:
            aggregated_speakers.append(speaker)
            content = get_content_of_segment(segment)
            aggregated_segments.append(content)

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


def get_content_of_segment(_segment):
    return _segment['alternatives'][0]['content']


def get_current_speaker(speakers, last_ind, current_data, last_speaker):
    try:
        if speakers[last_ind]['start_time'] <= float(current_data['start_time']) < speakers[last_ind]['end_time']:
            return speakers[last_ind]['speaker_label'], last_ind
        return speakers[last_ind + 1]['speaker_label'], last_ind + 1
    except:
        return last_speaker, last_ind


def get_speakers_labels(data):
    resultant = []
    for _data in data:
        resultant.append({'start_time': float(_data['start_time']),
                          'end_time': float(_data['end_time']),
                          'speaker_label': _data['speaker_label']})
    return resultant


if __name__ == '__main__':

    _data = json.load(codecs.open(folder_path + '\\' + file_name, 'r', 'utf-8-sig'))
    final = parse_amazon_transcribe_file(_data)
    with open('data_meeting_text_amazon_2.txt', 'w') as output_file:
        json.dump(final, output_file)
    with open('data_meeting_text_amazon2.csv', 'w') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(['sentence', 'speaker', 'dialogue_id'])
        for data in final:
            writer.writerow([data['sentence'],
                             data['speaker'],
                             data['dialogue_id']])
