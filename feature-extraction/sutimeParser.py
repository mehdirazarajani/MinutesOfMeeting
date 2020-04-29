import requests
import xmltodict
import json


def removeHeadTag(string):
    resultant = ''
    includeStr = True
    for line in string.split('\n'):
        if "<head>" in line:
            includeStr = False
            line = line.replace("<head>.*", "")
        if includeStr:
            resultant += (line + '\n')
        elif "</head>" in line:
            includeStr = True
    return resultant


def getUsefulData(string):
    resultant = ''
    includeStr = False
    for line in string.split('\n'):
        if "</table>" in line and includeStr:
            resultant += (line + '\n')
            break
        if includeStr:
            resultant += (line + '\n')
        if "<h3>Temporal Expressions</h3>" in line:
            includeStr = True
        if "<em>No temporal expressions.</em>" in line:
            resultant = ""
            break
    return resultant


def isWhenAnswerExists(string):
    return getUsefulData(string) != ""


def generatePayload(date_str: str, string: str) -> str:
    string = string.replace(" ", "%20")

    payloads = ['annotator=sutime',
                'rules=english',
                'relativeHeuristicLevel=NONE',
                'q=' + string,
                'd=' + date_str]
    return '&'.join(payloads)


def detectWhenAnswer(date,query):

    url = "http://nlp.stanford.edu:8080/sutime/process"

    payload = generatePayload(date, query)
    # 'd=2020-3-27&annotator=sutime&q=Last%20summer%2C%20they%20met%20every%20Tuesday%20afternoon%2C%20from%201%3A00%20pm%20to%203%3A00%20pm.hello%20world&rules=english&relativeHeuristicLevel=NONE'
    headers = {
        'Cookie': 'JSESSIONID=AB3C25D17EE35644316FEA443F50FFA4',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'JSESSIONID=9B04B88D40E69F5A58EF8B90AD602B2E'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    xml = response.text.encode('utf8')

    xml = getUsefulData(xml.decode("utf-8"))

    if xml == "":
        return False

    my_dict = xmltodict.parse(xml)
    json_data = json.dumps(my_dict)

    label = my_dict["table"]["tr"][0]
    data = my_dict["table"]["tr"][1:]

    return True, (query, data)
