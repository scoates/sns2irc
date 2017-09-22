import boto3
import hjson
import sys
import os

topic = os.environ.get('SNS2IRC_TOPIC', None)
if topic is None:
    config = hjson.load(open("zappa_settings.json"))
    topic = config["live"]["events"][0]["event_source"]["arn"]

client = boto3.client('sns')

response = client.publish(
    TopicArn=topic,
    Message=" ".join(sys.argv[1:])
)

print(topic, response)
