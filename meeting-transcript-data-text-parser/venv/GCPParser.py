import json

folder_path = 'D:\MinutesOfMeeting\meeting-audio-data'
file_name = 'GCP.txt'


def parse_GCP_transcribe_file(data):
    resultant = list()
    dialogue_id = 0
    for i in data:
        segment = i[:-1].replace('Transcript: ','')
        speaker_label = ''
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
        final = parse_GCP_transcribe_file(_data)
        with open('data_meeting_text_GCP.txt', 'w') as output_file:
            json.dump(final, output_file)