import csv
import re
import json

file_name = 'task_assign_raw_data.tsv'
clean_r = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')


def clean_html(raw_html):
    clean_text = re.sub(clean_r, '', raw_html)
    return clean_text


def extract_data_of_task():
    resultant = list()
    with open(file_name) as task_file:
        datas = csv.reader(task_file, delimiter='\t')
        for data in datas:
            data = data[1]
            res = dict()
            data = json.loads(data)
            res['subject'] = data['Subject']
            res['sender_name'] = data['From']['emailAddress']['Name']
            res['sender_email'] = data['From']['emailAddress']['Address']
            res['recipients_name'] = list()
            res['recipients_email'] = list()
            for _data in data['ToRecipients']['emailAddressList']:
                res['recipients_name'].append(_data['emailAddress']['Name'])
                res['recipients_email'].append(_data['emailAddress']['Address'])
            res['cc_name'] = list()
            res['cc_email'] = list()
            for _data in data['CcRecipients']['emailAddressList']:
                res['cc_name'].append(_data['emailAddress']['Name'])
                res['cc_email'].append(_data['emailAddress']['Address'])
            res['raw_msg'] = data['Message']
            res['processed_msg'] = clean_html(data['Message'])
            res['given_task_sentence'] = data['TaskSentence']
            resultant.append(res)
    return resultant


if __name__ == '__main__':

    with open('task_assign_processed_data.json', 'w') as output_file:
        json.dump(extract_data_of_task(), output_file)
