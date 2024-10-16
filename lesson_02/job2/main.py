import os
import re
import shutil
from dotenv import load_dotenv
from flask import Flask, request
import json
import fastavro
from fastavro import schema

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
        re_matched = re.search(fr'{BASE_DIR}/raw/sales/\d{{4}}-\d{{2}}-\d{{2}}', data['raw_dir'])
        if not re_matched:
            valid_msg['error'] = 1
            valid_msg['error_type'] = 'ValueError'
            valid_msg['msg'] = 'raw_dir does not match pattern'
            return valid_msg
    if 'stg_dir' not in data:
        valid_msg['error'] = 1
        valid_msg['error_type'] = 'ValueError'
        valid_msg['msg'] = 'stg_dir must be provided'
        return valid_msg
    else:
        re_matched = re.search(fr'{BASE_DIR}/stg/sales/\d{{4}}-\d{{2}}-\d{{2}}', data['stg_dir'])
        if not re_matched:
            valid_msg['error'] = 1
            valid_msg['error_type'] = 'ValueError'
            valid_msg['msg'] = 'stg_dir does not match pattern'
            return valid_msg

    raw_dir_date = re.findall(r'\d{4}-\d{2}-\d{2}', data['raw_dir'])
    stg_dir_date = re.findall(r'\d{4}-\d{2}-\d{2}', data['stg_dir'])
    if raw_dir_date[0] != stg_dir_date[0]:
        valid_msg['error'] = 1
        valid_msg['error_type'] = 'ValueError'
        valid_msg['msg'] = 'Date in raw path does not match to Date in stg path'
        return valid_msg

    return valid_msg


def move_to_stg(raw_dir: str, stg_dir: str):
    avro_schema = schema.load_schema(f'./data_schema.avsc')
    files = os.listdir(raw_dir)
    for file in files:
        with open(os.path.join(raw_dir, file), 'r', encoding='utf-8') as f:
            data = json.load(f)

        clear_directory(stg_dir)
        with open(os.path.join(stg_dir, file.replace('json', 'avro')), 'wb') as avro_file:
            fastavro.writer(avro_file, avro_schema, data)

    return data


@app.route('/job_2', methods=['POST'])
def job():
    request_data = request.get_json()
    valid_msg = params_validation(request_data)
    if valid_msg['error'] == 1:
        return valid_msg
    raw_dir = request_data['raw_dir']
    stg_dir = request_data['stg_dir']
    move_to_stg(raw_dir, stg_dir)

    return 'Success'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)
