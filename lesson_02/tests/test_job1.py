import pytest
from flask import json
from ..job1.main import app, params_validation, get_data
import os
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock

load_dotenv()
BASE_DIR = os.getenv('BASE_DIR')


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_post_request(client):
    response = client.post('/job_1',
                           data=json.dumps({"raw_dir": "some_path", "date": "2023-10-10"}),
                           content_type='application/json')
    assert response.status_code == 200


def test_params_validation_success():
    data = {"raw_dir": f"{BASE_DIR}/raw/sales/2024-10-17", "date": "2024-10-17"}
    result = params_validation(data)
    assert result['error'] == 0


def test_params_validation_missing_raw_dir():
    data = {
        "date": "2024-09-30"
    }
    result = params_validation(data)
    assert result['error'] == 1
    assert result['error_type'] == 'ValueError'
    assert result['msg'] == 'raw_dir must be provided'


def test_params_validation_invalid_date_format():
    data = {
        "raw_dir": f"{BASE_DIR}/raw/sales/2023-05-25",
        "date": "2023.05.25"
    }
    result = params_validation(data)
    assert result['error'] == 1
    assert result['error_type'] == 'DataTimeValueError'
    assert result['msg'] == 'Input parameters date must be yyyy-mm-dd format'


def test_params_validate_date_consistency():
    data = {
        "raw_dir": f"{BASE_DIR}/raw/sales/2023-02-30",
        "date": "2023-09-30"
    }
    result = params_validation(data)
    assert result['error'] == 1
    assert result['error_type'] == 'ValueError'
    assert result['msg'] == 'Date in path does not match to input parameter date'


@patch('requests.get')
def test_job_endpoint_success(mock_get, client, mocker):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {'Content-Type': 'application/json'}
    mock_response.json.return_value = [
        {"client": "Michael Wilkerson", "purchase_date": "2022-08-09", "product": "Vacuum cleaner", "price": 346},
        {"client": "Russell Hill", "purchase_date": "2022-08-09", "product": "Microwave oven", "price": 446}]
    mock_get.return_value = mock_response
    mocker.patch('os.makedirs')
    mocker.patch('shutil.rmtree')

    request_data = {
        "raw_dir": f"{BASE_DIR}/raw/sales/2022-08-09",
        "date": "2022-08-09"
    }
    response = client.post('/job_1',
                           data=json.dumps(request_data),
                           content_type='application/json')
    print('response', response)

    assert response.status_code == 200
    assert response.data == b'Success'
