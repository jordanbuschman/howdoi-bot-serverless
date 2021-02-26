import json
import logging
import os
import requests

from bs4 import BeautifulSoup as bs
from tomd import Tomd
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from urllib.parse import urlencode, parse_qs

logging.basicConfig()

PUBLIC_KEY = os.environ['PUBLIC_KEY']
RESPONSE_TYPES =  {
                    'PONG': 1,
                    'ACK_NO_SOURCE': 2,
                    'MESSAGE_NO_SOURCE': 3,
                    'MESSAGE_WITH_SOURCE': 4,
                    'ACK_WITH_SOURCE': 5
                  }

DDG_QUERY_URL = 'https://duckduckgo.com/html/?{}'
RESPONSE_MESSAGE = '**I interpreted your question as: "{}"**\n\n**Here\'s your answer:**\n{}'
NO_RESULTS_MESSAGE = 'Beep boop, no results found for "{}"'


def verify_signature(event):
    body = event['body']
    signature = event['headers'].get('x-signature-ed25519')
    timestamp  = event['headers'].get('x-signature-timestamp')

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature)) # raises an error if unequal

def ping_pong(body):
    if body.get('type') == RESPONSE_TYPES['PONG']:
        return True
    return False

def get_soup(url):
    page = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})
    return bs(page.text, features='html.parser')

def response(message):
    return {
        'type': RESPONSE_TYPES['MESSAGE_WITH_SOURCE'],
        'data': {
            'tts': False,
            'content': message,
        }
    }

def how_do_i(event, context):
    logger = logging.getLogger('howdoi')
    logger.setLevel(logging.DEBUG)

    logger.debug(f"event {event}")
    logger.debug(f"context {context}")

    # verify the signature
    try:
        verify_signature(event)
    except Exception as e:
        logger.error(f"[UNAUTHORIZED] Invalid request signature: {e}")
        return {}

    # check if message is a ping
    body = json.loads(event.get('body'))
    if ping_pong(body):
        return {
            'type': RESPONSE_TYPES['PONG']
        }

    query = body['data']['options'][0]['value'] + ' site:answers.yahoo.com'
    logger.debug(f"Got query: \"{query}\"")

    url = DDG_QUERY_URL.format(urlencode({'q': query}))
    soup = get_soup(url)
    
    # Get top 3 links
    ddg_links = [a.get('href') for a in soup.find_all('a', {'class': 'result__a'})][:5]
    # Parse out redirect link
    qss = [link.split('?')[1] for link in ddg_links]
    ya_links = [parse_qs(qs)['uddg'][0] for qs in qss]
    
    logger.debug(f"{len(ya_links)} links found")
    
    if not len(ya_links):
        logger.debug('No answers found')
        return response(NO_RESULTS_MESSAGE.format(query))
    
    # For each link, see if it's answered (has 1+ answer). Return the first one
    # found. If none are found in any links, return that no results are found
    for link in ya_links:
        soup = get_soup(link)
        
        top_answer = soup.find('div', {'class': lambda c: c is not None and c.startswith('Answer__answer___')})
        if top_answer is None:
            logger.debug('No top answer found')
            continue
            
        top_answer_body = top_answer.find('div', {'class': lambda c: c is not None and c.startswith('ExpandableContent__content___')})
        if top_answer_body is None:
            logger.debug('No top answer body found')
            continue
            
        ya_question = soup.find('h1', {'class': lambda c: c is not None and c.startswith('Question__title___')}).text
        str_answer = str(top_answer_body.encode_contents())
        md_answer = Tomd(str_answer).markdown
        
        logger.debug('Found answer')
        return response(RESPONSE_MESSAGE.format(ya_question, md_answer))
        
    logger.debug('No answers found')
    return response(NO_RESULTS_MESSAGE.format(query))