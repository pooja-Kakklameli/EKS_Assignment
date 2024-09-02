import os
import boto3

def handler(event, context):
    ssm = boto3.client('ssm')
    parameter_name = os.environ['SSM_PARAM_NAME']
    parameter = ssm.get_parameter(Name=parameter_name)
    environment = parameter['Parameter']['Value']

    # Set replicaCount based on environment
    if environment == 'development':
        replica_count = 1
    elif environment in ['staging', 'production']:
        replica_count = 2
    else:
        raise ValueError(f"Unknown environment: {environment}")

    return {
        "StatusCode": 200,
        "ReplicaCount": replica_count
    }
