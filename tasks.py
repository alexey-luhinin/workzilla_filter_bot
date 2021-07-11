import os.path
from datetime import datetime
import string
from typing import Dict, List, Union
import requests
from config import HEADERS


# Configurations
URL_GET = 'https://client.work-zilla.com/api/order/v1/list/open?sortOrder=0'
URL_TASK = 'https://client.work-zilla.com/freelancer/'
URL_REQUEST_DECLINE = 'https://client.work-zilla.com/api/order/v1/freelancer/decline'


keywords_for_search = ['python', 'flask', 'django', 'parse', 'selenium', 'bot',
                       'питон', 'парсинг', 'спарсить', 'бот',
                       'программирование', 'api', 'программист', 'web']


class Task:
    """"""

    def __init__(self, id: int, subject: str, description: str) -> None:
        self._id = id
        self._subject = subject
        self._description = description


    def find_work(self, keywords: List[str]) -> int:
        """Returns id of Task if description of Task has our keywords."""
        words_for_searching = (self._subject + ' ' + self._description).strip().split()

        for keyword in keywords:
            for word in words_for_searching:
                word = word.translate(str.maketrans('', '', string.punctuation)).strip()
                if keyword.lower() == word.lower():
                    return self._id


def get_list_of_tasks(URL_GET) -> List[Dict[str, Union[str, int]]]:
    """Send request to URL and returns list of tasks."""

    r = requests.get(URL_GET, headers=HEADERS)
    
    if r.status_code != 200:
        return r.status_code

    data = r.json()

    try:
        tasks = data['data']['other']
    except KeyError:
        print('No such key in dictionary!')
        exit()

    return tasks


def reject_the_tasks(tasks_ids: List[int], URL_REQUEST_DECLINE: str) -> None:
    """"""
    data = {"orderIds": tasks_ids} 

    r = requests.post(URL_REQUEST_DECLINE, headers=HEADERS, data=str(data))
    print(r.json())

    if r.status_code != 200:
        print(r.status_code); exit()


def write_to_file(path_to_file: str, record: str) -> None:
    """Write str to file."""
    with open(path_to_file, 'a') as f:
        f.write(record + '\n')


def read_from_file(path_to_file: str) -> List[str]:
    """Read file and returns List of lines."""
    with open(path_to_file, 'r') as f:
        return f.read().splitlines()


if __name__ == '__main__':

    while True:

        tasks_json = get_list_of_tasks(URL_GET)

        list_for_decline = []
        for task in tasks_json:
            id = Task(task['id'], task['subject'], task['description']).find_work(keywords_for_search)
            if id:
                links = []
                link = f'{URL_TASK}{id}'
                today = datetime.now()
                path = f'./tasks/{today.day}_{today.month}_{today.year}.txt'
                if os.path.isfile(path):
                    links = read_from_file(path)

                if link not in links:
                    write_to_file(path, link)
            else:
                list_for_decline.append(task['id'])
        reject_the_tasks(list_for_decline, URL_REQUEST_DECLINE)
