import boto3
import os

_cloudwatch_client = None


def aws_put_metric_heart_beat(value):
    if 'AWS_ACCESS_KEY_ID' not in os.environ:
        return

    global _cloudwatch_client
    if _cloudwatch_client is None:
        _cloudwatch_client = boto3.client('cloudwatch')
    cloudwatch = _cloudwatch_client

    # Put custom metrics
    cloudwatch.put_metric_data(
        MetricData=[
            {
                'MetricName': os.environ['PRICE_FEEDER_NAME'],
                'Dimensions': [
                    {
                        'Name': 'JOBS',
                        'Value': 'Error'
                    },
                ],
                'Unit': 'None',
                'Value': value
            },
        ],
        Namespace='MOC/EXCEPTIONS'
    )