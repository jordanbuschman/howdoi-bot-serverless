import json
import logging
import os
import requests

import boto3
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from src.response import get_follow_up, response, RESPONSE_TYPES

logging.basicConfig()

FOLLOW_UP_URL = 'https://discord.com/api/v8/webhooks/{}/{}/messages/@original'


def verify_signature(event):
    body = event['body']
    signature = event['headers'].get('x-signature-ed25519')
    timestamp  = event['headers'].get('x-signature-timestamp')

    verify_key = VerifyKey(bytes.fromhex(os.environ['PUBLIC_KEY']))
    verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature)) # raises an error if unequal

def ping_pong(body):
    if body.get('type') == RESPONSE_TYPES['PONG']:
        return True
    return False

def how_do_i(event, context):
    logger = logging.getLogger('howdoi')
    logger.setLevel(logging.DEBUG)

    logger.debug(f"event {event}")

    # verify the signature
    try:
        verify_signature(event)
    except Exception as e:
        logger.error(f"[UNAUTHORIZED] Invalid request signature: {e}")
        return {
            'message': 'Unauthorized'
        }

    # check if message is a ping
    body = json.loads(event.get('body'))
    if ping_pong(body):
        return {
            'type': RESPONSE_TYPES['PONG']
        }

    query = body['data']['options'][0]['value']
    logger.debug(f"Got query: \"{query}\"")

    # Send query to processing lambda to get processed
    processing_body = {
        'token': body['token'],
        'query': query,
        'application_id': os.environ['APPLICATION_ID']
    }

    logger.debug(f"Sending processing request for {processing_body}")
    client = boto3.client('lambda')
    client.invoke_async(
        FunctionName=os.environ['PROCESSING_ARN'],
        InvokeArgs=json.dumps(processing_body).encode('utf-8')
    )

    logger.debug('Done')
    return response(f"Searching for \"{query}\"...")

def process(event, context):
    logger = logging.getLogger('howdoi-processor')
    logger.setLevel(logging.DEBUG)

    logger.debug(f"event {event}")

    updated_answer = {
        'content': get_follow_up(event['query'] + ' site:answers.yahoo.com')
    }

    r = requests.patch(
        FOLLOW_UP_URL.format(event['application_id'], event['token']),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(updated_answer)
    )
    
    if r.status_code == 200:
        logger.debug('Sent message successfully')
    else:
        logger.debug(f"Discord responded with status code {r.status_code}: {r.text}")

    return {}