import logging
import os
import requests

from bs4 import BeautifulSoup as bs
from nacl.signing import VerifyKey

from src.constants import RESPONSE_TYPES


def get_soup(url: str) -> bs:
    page = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})
    return bs(page.text, features='html.parser')

def verify_signature(event: dict):
    body = event['body']
    signature = event['headers'].get('x-signature-ed25519')
    timestamp  = event['headers'].get('x-signature-timestamp')

    verify_key = VerifyKey(bytes.fromhex(os.environ['PUBLIC_KEY']))
    verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature)) # raises an error if unequal

def ping_pong(body: dict) -> bool:
    if body.get('type') == RESPONSE_TYPES['PONG']:
        return True
    return False

def discord_response(message: str) -> dict:
    return {
        'type': RESPONSE_TYPES['MESSAGE_WITH_SOURCE'],
        'data': {
            'tts': False,
            'content': message,
        }
    }