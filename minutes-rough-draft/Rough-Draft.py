import json


def get_file_content(filename: str) -> json:
    with open(filename) as file_data:
        _data = json.load(file_data)

    return _data


if __name__ == '__main__':
    clusters = get_file_content('clusters.txt')
    importants = get_file_content('important-sentence.txt')
    question_answers = get_file_content('question-answer-pairs.txt')

    important_question_answers_id_map = {qa['dialogue_id']: qa for qa in question_answers}

    resultants = {}
    for i in range(0, len(clusters)):
        cluster_data = clusters[i]
        important_data = importants[i]
        id = important_data['dialogue_id']

        cluster = cluster_data['cluster']
        classification_type = str(important_data['classification_type'])
        if classification_type.startswith("Interrogative"):
            classification_type = "Questions Answers"

        if classification_type == "Questions Answers" and id in important_question_answers_id_map:
            question_answer = important_question_answers_id_map[id]
            if cluster not in resultants:
                resultants[cluster] = {'Normal': [], 'Suggestion': [], 'Task Assigned': [], 'Questions Answers': []}
            resultants[cluster][classification_type].append({'dialogue_id': important_data['dialogue_id'],
                                                             'sentence': question_answer['question'],
                                                             'speaker': important_data['speaker'],
                                                             'score': important_data['score'],
                                                             'cluster': cluster,
                                                             'result': question_answer['result'],
                                                             'classification_type': classification_type})
        elif important_data['is_important'] and classification_type != "Questions Answers":
            if cluster not in resultants:
                resultants[cluster] = {'Normal': [], 'Suggestion': [], 'Task Assigned': [], 'Questions Answers': []}
            resultants[cluster][classification_type].append({'dialogue_id': important_data['dialogue_id'],
                                                             'sentence': important_data['sentence'],
                                                             'speaker': important_data['speaker'],
                                                             'score': important_data['score'],
                                                             'cluster': cluster,
                                                             'classification_type': classification_type})

    with open('rough draft.txt', 'w') as output_file:
        json.dump(resultants, output_file)
