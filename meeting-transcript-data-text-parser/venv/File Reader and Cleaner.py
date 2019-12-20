import json
import re
from jellyfish import jaro_distance

folder_path = 'D:\\Meeting Transcript Data\\updated'
file_name = 'meetingtranscript566.txt'
file_hierarchy = [{'starting_indicator': '', 'type': 'metadata_texts', 'is_extendable': False},
                  {'starting_indicator': 'ATTENDANCE:', 'type': 'attendees', 'is_extendable': False},
                  {'starting_indicator': 'C O N T E N T', 'type': 'agenda_texts', 'is_extendable': False},
                  {'starting_indicator': 'P R O C E E D I N G', 'type': 'meeting_texts', 'is_extendable': True}]
attendees_hierarchy = [{'starting_indicator': 'Members/Alternates:', 'child': ['Management Members', 'Labor Members'],
                        'starts_new_line': True},
                       {'starting_indicator': 'Staff Specialists and Visitors:', 'child': [], 'starts_new_line': True},
                       {'starting_indicator': 'Recording Secretary:', 'child': [], 'starts_new_line': False}]
agenda_hierarchy = [{'starting_indicator': 'Opening/Announcements', 'hierarchy': ['â€¢', '-']},
                    {'starting_indicator': 'Review of the Minutes of', 'hierarchy': []},
                    {'starting_indicator': 'Old Business', 'hierarchy': ['a.', '-']},
                    {'starting_indicator': 'New Business', 'hierarchy': ['a.', '-']}]
agenda_hierarchy_list = ['Opening/Announcements', 'Review of the Minutes of', 'Old Business', 'New Business']
replace = {'’': "'"}
regex_replace = {r'''\[([^\]]*)\]''': '', r'[^\x00-\x7F]+': '', r'^[a-z]\.': ''}
sentence_regex = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'
agenda_code_regex = r'\d{2,}-\w{2,}-\d{1,}'
speaker_regex = r'^([A-Z]{2,}\.|CHAIRMAN) [A-Z]{3,}\:'
speaker_regex1 = r'^[A-Z\. ]{2,}:'


def read_from_file():
    hierarchy_index = 0
    page_number = ''
    resultant = {}
    for hierarchy in file_hierarchy:
        resultant[hierarchy['type']] = []

    with open(folder_path + "\\" + file_name) as text_file:
        for line in text_file:
            line_str = line.strip()
            line_str = replace_str(line_str)
            # line_str = replace_str_regex(line_str)
            if line_str == '' or line_str == 'Page':
                continue
            if line_str.isdigit():
                page_number = line_str
                continue
            if '(continued)' in line_str:
                continue
            if len(file_hierarchy) > hierarchy_index + 1 and line_str.startswith(file_hierarchy[hierarchy_index + 1][
                'starting_indicator']):
                hierarchy_index += 1
                continue
            if file_hierarchy[hierarchy_index]['is_extendable']:
                if ':' in line_str or len(resultant[file_hierarchy[hierarchy_index]['type']]) == 0:
                    resultant[file_hierarchy[hierarchy_index]['type']].append(page_number + '#' + line_str)
                else:
                    resultant[file_hierarchy[hierarchy_index]['type']][-1] += (' ' + line_str)
            else:
                resultant[file_hierarchy[hierarchy_index]['type']].append(page_number + '#' + line_str)
    return resultant


def replace_str(line):
    for (key, value) in replace.items():
        line = line.replace(key, value)
    return line


def replace_str_regex(line):
    for (key, value) in regex_replace.items():
        line = re.sub(key, value, line)
    return line


def structure_the_agenda_data(title, data):
    resultants = {}
    hierarchy_index = -1
    nested_index = -1
    last_bullet = ''
    full_agenda = ''
    last_header = ''

    for hierarchy in agenda_hierarchy:
        resultants[hierarchy['starting_indicator']] = []

    for ind, line in enumerate(data):
        if len(agenda_hierarchy) > hierarchy_index + 1 and '.' in line and \
                line.split('.')[1].strip().startswith(agenda_hierarchy[hierarchy_index + 1]['starting_indicator']):
            if full_agenda != '':
                resultants[hierarchy['starting_indicator']].append({'page_num': -1, 'text': full_agenda})
            hierarchy_index += 1
            nested_index = -1
            full_agenda = ''
            last_header = ''
            last_bullet = ''
            if len(agenda_hierarchy[hierarchy_index]['hierarchy']) == 0:
                page_num = -1
                if '.' in line:
                    page_num = line.split('.')[-1]
                    line = line.split('.')[1].strip()
                    line = line.split('.')[0]
                resultants[agenda_hierarchy[hierarchy_index]['starting_indicator']].append(
                    {'page_num': page_num, 'text': line})
            continue
        line = line.split('#')[1]
        if hierarchy_index == -1:
            continue
        hierarchy = agenda_hierarchy[hierarchy_index]
        if len(hierarchy['hierarchy']) > nested_index + 1 and line.startswith(hierarchy['hierarchy'][nested_index + 1]):
            if full_agenda != '':
                last_header = full_agenda[:]
            nested_index += 1
            if hierarchy['hierarchy'][nested_index] == 'a.':
                last_bullet = hierarchy['hierarchy'][nested_index]
            if re.search(r'\.\d+$', line):
                page_num = line.split('.')[-1]
                if '.' in last_bullet:
                    line = line.split('.')[0] + ' ' + line.split('.')[1]
                else:
                    line = line.split('.')[0]
                full_agenda += (' ' + line)
                resultants[hierarchy['starting_indicator']].append({'page_num': page_num, 'text': full_agenda})
                full_agenda = ''  # ''
                continue
            elif nested_index == 0:
                full_agenda = line[:]
            else:
                full_agenda += (' ' + line)
        elif nested_index != -1 and line.startswith(
                next_hierarchy_bullet(hierarchy['hierarchy'][nested_index - 1], last_bullet)):
            if full_agenda != '':
                resultants[hierarchy['starting_indicator']].append({'page_num': -1, 'text': full_agenda})
                full_agenda = line  # ''
            if hierarchy['hierarchy'][nested_index - 1] == 'a.':
                last_bullet = next_hierarchy_bullet(hierarchy['hierarchy'][nested_index - 1], last_bullet)
            if nested_index == 0:
                last_header = ''
            nested_index -= 1
            if re.search(r'\.\d+$', line):
                page_num = line.split('.')[-1]
                if '.' in last_bullet:
                    line = line.split('.')[0] + ' ' + line.split('.')[1]
                else:
                    line = line.split('.')[0]
                full_agenda = line
                resultants[hierarchy['starting_indicator']].append({'page_num': page_num, 'text': full_agenda})
                continue
            else:
                full_agenda = line[:]
        elif line.startswith(next_hierarchy_bullet(hierarchy['hierarchy'][nested_index], last_bullet)):
            if full_agenda != '':
                resultants[hierarchy['starting_indicator']].append({'page_num': -1, 'text': full_agenda})
                full_agenda = last_header[:]  # ''
            if hierarchy['hierarchy'][nested_index] == 'a.':
                last_bullet = next_hierarchy_bullet(hierarchy['hierarchy'][nested_index], last_bullet)
            if nested_index == 0:
                last_header = ''
            if re.search(r'\.\d+$', line):
                page_num = line.split('.')[-1]
                if '.' in last_bullet:
                    line = line.split('.')[0] + ' ' + line.split('.')[1]
                else:
                    line = line.split('.')[0]
                full_agenda += (' ' + line)
                resultants[hierarchy['starting_indicator']].append({'page_num': page_num, 'text': full_agenda})
                continue
            else:
                full_agenda = last_header + ' ' + line

        elif re.search(r'\.\d+$', line):
            page_num = line.split('.')[-1]
            if '.' in last_bullet:
                line = line.split('.')[0] + ' ' + line.split('.')[1]
            else:
                line = line.split('.')[0]
            full_agenda += (' ' + line)
            resultants[hierarchy['starting_indicator']].append({'page_num': page_num, 'text': full_agenda})
            full_agenda = ''
            continue
        else:
            full_agenda += (' ' + line)
    return {("structured_" + title): resultants}


def improve_agenda_data(title, data):
    resultants = {}
    not_done = set()
    last_starting_page_number = 0
    last_ending_page_number = 0

    for hierarchy in agenda_hierarchy:
        resultants[hierarchy['starting_indicator']] = []
        not_done.add(hierarchy['starting_indicator'])

    for key, values in data.items():
        for ind, value in enumerate(values):
            resultant = {}
            # last_ending_page_number = last_starting_page_number
            text = replace_str_regex(value['text']).strip()
            if re.search(agenda_code_regex,text):
                codes = re.findall(agenda_code_regex,text)
                for i,_text in enumerate(re.split(agenda_code_regex,text)):
                    if replace_str_regex(_text).strip() == '':
                        continue
                    if value['page_num'] != -1:
                        last_starting_page_number = value['page_num']
                    resultant['starting_page_num'] = last_starting_page_number
                    resultant['ending_page_num'] = -2
                    resultant['text'] = replace_str_regex(_text).strip()
                    if len(codes) > i:
                        resultant['code'] = codes[i]
                    else:
                        resultant['code'] = ''
                    resultants[key].append(resultant)
            else:
                if value['page_num'] != -1:
                    last_starting_page_number = value['page_num']
                resultant['starting_page_num'] = last_starting_page_number
                resultant['ending_page_num'] = -2
                resultant['text'] = replace_str_regex(value['text']).strip()
                resultant['code'] = ''
                resultants[key].append(resultant)
                # add ending_page_num to all previous
                for i in range(ind - 1, -1, -1):
                    if resultants[key][i]['ending_page_num'] == -2:
                        resultants[key][i]['ending_page_num'] = last_starting_page_number
        done = set()
        for remaining_key in not_done:
            for i in range(len(resultants[remaining_key]) - 1, -1, -1):
                if resultants[key][i]['ending_page_num'] == -2:
                    resultants[key][i]['ending_page_num'] = last_starting_page_number
            if len(resultants[remaining_key]) > 0:
                done.add(remaining_key)
        not_done = set.difference(not_done, done)

    for i, hierarchy in enumerate(agenda_hierarchy_list[:-1]):
        inc_value = 1
        if len(agenda_hierarchy_list) <= i + inc_value:
            break
        if len(resultants[agenda_hierarchy_list[i+inc_value]]) == 0:
            inc_value += 1
        else:
            resultants[hierarchy][-1]['ending_page_num'] = resultants[agenda_hierarchy_list[i+inc_value]][0]['starting_page_num']

    dec_value = 1
    for i in range(len(agenda_hierarchy_list) -1, 0, -1):
        hierarchy = agenda_hierarchy_list[i]
        if (len(resultants[hierarchy])) > 0:
            break
        dec_value += 1
    resultants[agenda_hierarchy_list[-dec_value]][-1]['ending_page_num'] = -2

    return {("structured_" + title): resultants}


def next_hierarchy_bullet(bullet, last):
    if bullet == 'a.':
        return chr(ord(last[0]) + 1) + '.'
    return bullet


def structure_the_meetings_data(title, data):
    resultants = []
    dialogue_id = 0
    for ind, dialogue in enumerate(data):
        page_number = dialogue.split("#")[0]
        dialogue = dialogue.split('#')[1]
        if re.search(speaker_regex1, dialogue):
            speaker = re.findall(speaker_regex1, dialogue)[0]
            a = re.split(speaker_regex1, dialogue)
            sentences = re.split(sentence_regex, replace_str_regex(a[1]).strip())
            for sentence in sentences:
                resultant = dict()
                resultant['sentence'] = replace_str_regex(sentence).strip()
                resultant['speaker'] = speaker
                resultant['dialogue_id'] = dialogue_id
                resultant['page_number'] = page_number
                resultants.append(resultant)
            dialogue_id += 1
        else:
            speaker = resultants[-1]['speaker']
            dialogue_id = resultants[-1]['dialogue_id']
            sentences = re.split(sentence_regex, replace_str_regex(dialogue).strip())
            resultants[-1]['sentence'] += ' ' + sentences[0]
            for sentence in sentences[1:]:
                resultant = dict()
                resultant['sentence'] = replace_str_regex(sentence).strip()
                resultant['speaker'] = speaker
                resultant['dialogue_id'] = dialogue_id
                resultant['page_number'] = page_number
                resultants.append(resultant)
            pass
    return {("structured_" + title): resultants}


def structure_the_attendees_data(title, data):
    resultants = {}
    hierarchy_index = -1
    nested_index = -1

    for hierarchy in attendees_hierarchy:
        if len(hierarchy['child']) > 0:
            resultants[hierarchy['starting_indicator']] = {}
            for child in hierarchy['child']:
                resultants[hierarchy['starting_indicator']][child] = []
        else:
            resultants[hierarchy['starting_indicator']] = []

    for line in data:
        line = replace_str_regex(line).split('#')[1]
        if len(attendees_hierarchy) > hierarchy_index + 1 and attendees_hierarchy[hierarchy_index + 1][
            'starting_indicator'] in line:
            hierarchy_index += 1
            nested_index = -1
            if attendees_hierarchy[hierarchy_index]['starts_new_line']:
                continue
            else:
                line = line.replace(attendees_hierarchy[hierarchy_index]['starting_indicator'], '').strip()
        hierarchy = attendees_hierarchy[hierarchy_index]
        if len(hierarchy['child']) > 0:
            if len(hierarchy['child']) > nested_index + 1 and line == hierarchy['child'][nested_index + 1]:
                nested_index += 1
                continue
            if ', ' in line:
                name = line.split(', ')
                resultants[hierarchy['starting_indicator']][hierarchy['child'][nested_index]].append(
                    {'person_name': name[0], 'department_name': name[1]})
            else:
                resultants[hierarchy['starting_indicator']][hierarchy['child'][nested_index]].append(
                    {'person_name': line, 'department_name': ''})
        else:
            if ', ' in line:
                name = line.split(', ')
                resultants[hierarchy['starting_indicator']].append(
                    {'person_name': name[0], 'department_name': name[1]})
            else:
                resultants[hierarchy['starting_indicator']].append(
                    {'person_name': line, 'department_name': ''})
    return {("structured_" + title): resultants}


def arr_to_str(array, delimiter):
    resultant = array[0]
    for _res in array[1:]:
        resultant += (delimiter + _res)
    return resultant


def remove_introduction_part1(attendees, sentences):
    end_introduction_index = 0
    is_introduction_started = False
    indications_of_starting_introduction = ['Welcome', 'welcome', 'introduce', 'introduction']
    introduction_starting_index = 0

    for ind, sentence in enumerate(sentences):
        if not is_introduction_started:
            for indication in indications_of_starting_introduction:
                if indication in sentence:
                    is_introduction_started = True
                    introduction_starting_index = ind
                    break
        if introduction_starting_index == ind:
            continue
        if is_introduction_started:
            temp = sentence.split(':')
            speaker = temp[0].strip()
            sentence_ = temp[1].strip()
            if speaker.split(' ')[1].title() in sentence_ and jaro_distance(speaker.split(' ')[1].title(), sentence_):
                continue
            end_introduction_index = ind
            break
    return sentences[end_introduction_index + 1:]


def remove_introduction_part(sentences, max_space=5):
    last_attendee_found = 0
    for ind, sentence in enumerate(sentences):
        if ind - last_attendee_found >= max_space:
            break
        temp = sentence.split(':')
        speaker = temp[0].strip()
        sentence_ = temp[1].strip()
        if speaker.split(' ')[1].title() in sentence_ and jaro_distance(speaker.split(' ')[1].title(), sentence_):
            last_attendee_found = ind
    return sentences[last_attendee_found + 1:]


def get_attendees(attendees_text):
    attendees = []
    for key, values in attendees_text.items():
        if type(values) == list:
            for value in values:
                attendees.append(value['person_name'])
        elif type(values) == dict:
            for _key, _values in values.items():
                if type(_values) == list:
                    for _value in _values:
                        attendees.append(_value['person_name'])

    return attendees


if __name__ == '__main__':
    with open('data.txt', 'w') as outfile:
        resultant = read_from_file()
        json.dump(resultant, outfile)
        meeting_text = structure_the_meetings_data('meeting_texts', resultant['meeting_texts'])
        attendees_text = structure_the_attendees_data('attendees', resultant['attendees'])
        attendees = get_attendees(attendees_text['structured_attendees'])
        agenda_text = structure_the_agenda_data('agenda_texts', resultant['agenda_texts'])
        improved_agenda_text = improve_agenda_data('agenda_texts', agenda_text['structured_agenda_texts'])
        with open('data_meeting_text.txt', 'w') as outfile1:
            json.dump(meeting_text, outfile1)
        with open('data_attendees.txt', 'w') as outfile1:
            json.dump(attendees_text, outfile1)
        with open('data_meeting_text1.txt', 'w') as outfile1:
            data = structure_the_meetings_data('meeting_texts_without_introduction',
                                               remove_introduction_part(resultant['meeting_texts']))
            json.dump(data, outfile1)
        with open('data_agenda.txt', 'w') as outfile1:
            json.dump(agenda_text, outfile1)
        with open('data_agenda1.txt', 'w') as outfile1:
            json.dump(improved_agenda_text, outfile1)
