from random import randint
import datetime
import boto3
import json
import os
from boto3.dynamodb.conditions import Key, Attr
from requests_oauthlib import OAuth1Session

DIFF_JST_FROM_UTC = 9

# Env variables
consumer_key = os.environ['CONSUMER_KEY']
client_secret_key = os.environ['CLIENT_SECRET_KEY']
access_token = os.environ['ACCESS_TOKEN']
access_token_secret = os.environ['ACCESS_TOKEN_SECRET']

oauth = OAuth1Session(consumer_key, client_secret_key, access_token, access_token_secret)
dynamodb = boto3.resource('dynamodb')

def lambda_function(event, context):
    # Table difinition
    table_name = 'x_bot_message'
    table = dynamodb.Table(table_name)
    
    # Retrieve data from dynamoDB
    res = table.get_item(Key={'x_bot_message_id': 1})
    text = res["Item"]["x_bot_message"]
    
    # Add datetime to avoid duplicate content
    local_date_time = datetime.datetime.now()
    japanese_local_date_time = local_date_time + datetime.timedelta(hours=DIFF_JST_FROM_UTC) 
    display_local_datetime = japanese_local_date_time.strftime('%Y年%m月%d日 %H:%M:%S')
    tweet_content = text + '\n' + display_local_datetime
    
    # Process tweet
    payload = {'text': tweet_content}
    response = oauth.post("https://api.twitter.com/2/tweets", json=payload)
    
    if response.status_code == 201:
        print('Success')
    else:
        raise Exception(
            "[Error] {} {}".format(response.status_code, response.text)
        )

    return response.status_code
