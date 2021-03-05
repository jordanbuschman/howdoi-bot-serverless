import json
import logging
import os

import boto3

from src.constants import RESPONSE_TYPES
from src.utils import ping_pong, discord_response, verify_signature

logging.basicConfig()


def input_handler(event: dict, context: dict) -> dict:
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
    return discord_response(f"Searching for \"{query}\"...")