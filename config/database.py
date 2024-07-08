# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/

import os

import boto3
from botocore.exceptions import ClientError


def get_secret():
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=os.environ.get("REGION"),
        aws_access_key_id=os.environ.get("ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("SECRET_KEY"),
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=os.environ.get("SECRET_NAME")
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response["SecretString"]

    return secret
