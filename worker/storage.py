import os
import boto3
import botocore
import json


def read(key, default_value=None):
    try:
        s3 = boto3.client('s3')

        response = s3.get_object(
            Bucket=os.environ['S3_BUCKET'],
            Key='{}.json'.format(key)
        )

        body = response['Body'].read()

        return json.loads(body.decode('utf-8'))
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'NoSuchKey' and default_value is not None:
            return default_value
        else:
            raise error


def write(key, data):
    s3 = boto3.client('s3')

    response = s3.put_object(
        Bucket=os.environ['S3_BUCKET'],
        Key='{}.json'.format(key),
        Body=json.dumps(data),
        ContentEncoding='utf-8',
        ContentType='application/json'
    )


class Storage():
    def __init__(self, key, default_value=None):
        self.key = key
        self.default_value = default_value

    def read(self):
        return read(self.key, default_value=self.default_value)

    def write(self, data):
        return write(self.key, data)
