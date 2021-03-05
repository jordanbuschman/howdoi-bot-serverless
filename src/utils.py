import logging
import os
import requests

from bs4 import BeautifulSoup as bs
from nacl.signing import VerifyKey

from src.constants import RESPONSE_TYPES


def get_soup(url):
    page = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})
    return bs(page.text, features='html.parser')

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

def discord_response(message):
    return {
        'type': RESPONSE_TYPES['MESSAGE_WITH_SOURCE'],
        'data': {
            'tts': False,
            'content': message,
        }
    }