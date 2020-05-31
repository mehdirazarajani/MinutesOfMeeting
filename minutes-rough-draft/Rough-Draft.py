import json


def get_file_content(filename: str) -> json:
    with open(filename) as file_data:
        _data = json.load(file_data)

    return _data


if __name__ == '__main__':
    clusters = get_file_content('clusters.txt')
    classifications = get_file_content('classification.json')
    impotants = get_file_content('important-sentence.txt')
    
    print(1)
