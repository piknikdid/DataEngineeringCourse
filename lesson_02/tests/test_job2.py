import pytest
from flask import json
from ..job2.main import app, params_validation, move_to_stg
import os
from dotenv import load_dotenv
from unittest.mock import patch, mock_open
from fastavro.schema import load_schema

load_dotenv()
BASE_DIR = os.getenv('BASE_DIR')


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_post_request(client):
    response = client.post('/job_2',
                           data=json.dumps({"raw_dir": "raw_path", "stg_dir": "stg_path"}),
                           content_type='application/json')
    assert response.status_code == 200


def test_params_validation_success():
    data = {"raw_dir": f"{BASE_DIR}/raw/sales/2024-10-16", "stg_dir": f"{BASE_DIR}/stg/sales/2024-10-16"}
    result = params_validation(data)
    assert result['error'] == 0


def test_params_validation_missing_raw_dir():
    data = {
        "stg_dir": f"{BASE_DIR}/stg/sales/2024-10-16"
    }
    result = params_validation(data)
    assert result['error'] == 1
    assert result['error_type'] == 'ValueError'
    assert result['msg'] == 'raw_dir must be provided'


def test_params_validation_missing_stg_dir():
    data = {
        "raw_dir": f"{BASE_DIR}/raw/sales/2024-10-16"
    }
    result = params_validation(data)
    assert result['error'] == 1
    assert result['error_type'] == 'ValueError'
    assert result['msg'] == 'stg_dir must be provided'


def test_params_validate_date_consistency():
    data = {
        "raw_dir": f"{BASE_DIR}/raw/sales/2023-02-30",
        "stg_dir": f"{BASE_DIR}/stg/sales/2024-10-16"
    }
    result = params_validation(data)
    assert result['error'] == 1
    assert result['error_type'] == 'ValueError'
    assert result['msg'] == 'Date in raw path does not match to Date in stg path'

def test_params_validation_invalid_raw_dir():
    data = {"raw_dir": "invalid_path", "stg_dir": f"{BASE_DIR}/stg/sales/2023-09-30"}
    result = params_validation(data)
    assert result['error'] == 1
    assert result['msg'] == 'raw_dir does not match pattern'


def test_params_validation_invalid_stg_dir():
    data = {"raw_dir": f"{BASE_DIR}/raw/sales/2023-09-30", "stg_dir": "invalid_path"}
    result = params_validation(data)
    assert result['error'] == 1
    assert result['msg'] == 'stg_dir does not match pattern'


@patch('os.listdir', return_value=['data1.json', 'data2.json'])
@patch('builtins.open', new_callable=mock_open)
@patch('fastavro.writer')
@patch('fastavro.schema.load_schema')
def test_move_to_stg(mock_load_schema, mock_fastavro_writer, mock_open, mock_listdir, mocker):
    mock_schema = {
        "type": "record",
        "name": "AvroSchema",
        "fields": [
            {"name": "client", "type": "string"},
            {"name": "purchase_date", "type": "string"},
            {"name": "product", "type": "string"},
            {"name": "price", "type": "int"}
        ]
    }
    mock_load_schema.return_value = mock_schema
    raw_dir = f'{BASE_DIR}/raw/sales/2022-08-09'
    stg_dir = f'{BASE_DIR}/stg/sales/2022-08-09'

    mocker.patch('os.makedirs')
    mocker.patch('shutil.rmtree')

    mock_open().read.side_effect = [
        json.dumps([{"client": "Client A", "purchase_date": "2023-09-30", "product": "Product A", "price": 100}]),
        json.dumps([{"client": "Client B", "purchase_date": "2023-09-30", "product": "Product B", "price": 200}])
    ]

    result = move_to_stg(raw_dir, stg_dir)

    assert mock_fastavro_writer.call_count == 2
    assert mock_fastavro_writer.call_args_list[0][0][0].name.endswith('.avro')
    assert mock_fastavro_writer.call_args_list[1][0][0].name.endswith('.avro')


