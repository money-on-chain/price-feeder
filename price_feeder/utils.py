import boto3
import os


def aws_put_metric_heart_beat(value):
    if 'AWS_ACCESS_KEY_ID' not in os.environ:
        return

    # Create CloudWatch client
    cloudwatch = boto3.client('cloudwatch')

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