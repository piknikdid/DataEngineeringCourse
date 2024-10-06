import os
import re
import shutil
import requests
from dotenv import load_dotenv
from flask import Flask, request
from datetime import datetime
import json

app = Flask(__name__)

load_dotenv()

AUTH_TOKEN = os.getenv('AUTH_TOKEN')
BASE_DIR = os.getenv('BASE_DIR')


def clear_directory(directory_path):
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
    os.makedirs(directory_path)


def params_validation(data: dict) -> dict:
    valid_msg = {"error": 0, "error_type": '', "msg": ''}
    if 'raw_dir' not in data:
        valid_msg['error'] = 1
        valid_msg['error_type'] = 'ValueError'
        valid_msg['msg'] = 'raw_dir must be provided'
        return valid_msg
    else:
        re_matched = re.search(r'.+raw/sales/\d{4}-\d{2}-\d{2}', data['raw_dir'])
        if not re_matched:
            valid_msg['error'] = 1
            valid_msg['error_type'] = 'ValueError'
            valid_msg['msg'] = 'raw_dir does not match pattern'
            return valid_msg
    if 'date' not in data:
        valid_msg['error'] = 1
        valid_msg['error_type'] = 'ValueError'
        valid_msg['msg'] = 'date must be provided'
        return valid_msg
    else:
        try:
            datetime.strptime(data['date'], '%Y-%m-%d')
        except Exception as e:
            valid_msg['error'] = 1
            valid_msg['error_type'] = 'DataTimeValueError'
            valid_msg['msg'] = 'Input parameters date must be yyyy-mm-dd format'
            return valid_msg

    pattern_date = re.findall(r'\d{4}-\d{2}-\d{2}', data['raw_dir'])
    if pattern_date[0] != data['date']:
        valid_msg['error'] = 1
        valid_msg['error_type'] = 'ValueError'
        valid_msg['msg'] = 'Date in path does not match to input parameter date'
        return valid_msg

    return valid_msg


def get_data(date: str):
    page = 1
    data = []
    message = ''
    while message == '':
        response = requests.get(
            url='https://fake-api-vycpfa6oca-uc.a.run.app/sales',
            params={'date': date, 'page': page},
            headers={'Authorization': AUTH_TOKEN},
        )
        if response.status_code == 200:
            response_data = response.json()
        else:
            message = 'Request failed'
        if 'message' in response_data:
            message = response_data['message']
        elif 'error' in response_data:
            message = response_data['error']
        else:
            data = data + response_data
            page += 1

    return data


@app.route('/job_1', methods=['POST'])
def job():
    request_data = request.get_json()
    valid_msg = params_validation(request_data)
    if valid_msg['error'] == 1:
        return valid_msg
    raw_dir = request_data['raw_dir']
    date = request_data['date']
    json_data = get_data(date)

    clear_directory(raw_dir)

    with open(raw_dir + f'/{date}.json', 'w', encoding='utf') as f:
        json.dump(json_data, f)

    return 'Success'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
