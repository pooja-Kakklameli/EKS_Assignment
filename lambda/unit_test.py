import boto3
import pytest
from botocore.stub import Stubber
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../lambda'))
import index  # Ensure this is your Lambda function file

@pytest.fixture
def mock_ssm(monkeypatch):
    # Mock the boto3.client call
    ssm_client = boto3.client('ssm')
    stubber = Stubber(ssm_client)
    monkeypatch.setattr(boto3, 'client', lambda service_name, *args, **kwargs: ssm_client)
    return stubber

def test_handler_development(mock_ssm, monkeypatch):
    # Mock the get_parameter call for the 'development' environment
    mock_ssm.add_response('get_parameter', {
        'Parameter': {
            'Value': 'development'
        }
    }, {'Name': 'mock_param_name'})

    mock_ssm.activate()
    monkeypatch.setenv('SSM_PARAM_NAME', 'mock_param_name')

    # Call the handler and check the result
    result = index.handler({}, {})
    assert result['ReplicaCount'] == 1  # Use correct key 'ReplicaCount'

    mock_ssm.deactivate()

def test_handler_production(mock_ssm, monkeypatch):
    # Mock the get_parameter call for the 'production' environment
    mock_ssm.add_response('get_parameter', {
        'Parameter': {
            'Value': 'production'
        }
    }, {'Name': 'mock_param_name'})

    mock_ssm.activate()
    monkeypatch.setenv('SSM_PARAM_NAME', 'mock_param_name')

    # Call the handler and check the result
    result = index.handler({}, {})
    assert result['ReplicaCount'] == 2  # Use correct key 'ReplicaCount'

    mock_ssm.deactivate()


def test_handler_staging(mock_ssm, monkeypatch):
    
    mock_ssm.add_response('get_parameter', {
        'Parameter': {
            'Value': 'staging'
        }
    }, {'Name': 'mock_param_name'})

    mock_ssm.activate()
    monkeypatch.setenv('SSM_PARAM_NAME', 'mock_param_name')

    # Call the handler and check the result
    result = index.handler({}, {})
    assert result['ReplicaCount'] == 2  

    mock_ssm.deactivate()


def test_handler_unknown_environment(mock_ssm, monkeypatch):
    # Mock the get_parameter call for an 'unknown' environment
    mock_ssm.add_response('get_parameter', {
        'Parameter': {
            'Value': 'unknown'
        }
    }, {'Name': 'mock_param_name'})

    mock_ssm.activate()
    monkeypatch.setenv('SSM_PARAM_NAME', 'mock_param_name')

    # Check if ValueError is raised for an unknown environment
    with pytest.raises(ValueError, match="Unknown environment: unknown"):
        index.handler({}, {})

    mock_ssm.deactivate()
