import json
import logging
import os
import requests

from tomd import Tomd
from urllib.parse import urlencode, parse_qs

from src.constants import NO_RESULTS_MESSAGE, RESPONSE_MESSAGE, FOLLOW_UP_URL, DDG_QUERY_URL
from src.utils import get_soup


logging.basicConfig()


def get_follow_up(query):
    logger = logging.getLogger('follow-up')
    logger.setLevel('DEBUG')

    url = DDG_QUERY_URL.format(urlencode({'q': query + ' site:answers.yahoo.com'}))
    soup = get_soup(url)

    # Get top 3 links
    ddg_links = [a.get('href') for a in soup.find_all('a', {'class': 'result__a'})][:5]
    # Parse out redirect link
    qss = [link.split('?')[1] for link in ddg_links]
    ya_links = [parse_qs(qs)['uddg'][0] for qs in qss]

    logger.debug(f"{len(ya_links)} links found")
 
    if not len(ya_links):
        logger.debug('No answers found')
        return NO_RESULTS_MESSAGE.format(query)

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
        str_answer = top_answer_body.encode_contents(formatter=None).decode("utf-8").strip()
        md_answer = Tomd(str_answer).markdown.strip()

        logger.debug('Found answer')
        return RESPONSE_MESSAGE.format(ya_question, md_answer).strip()

    logger.debug('No answers found')
    return NO_RESULTS_MESSAGE.format(query)

def response_handler(event, context):
    logger = logging.getLogger('howdoi-processor')
    logger.setLevel(logging.DEBUG)

    logger.debug(f"event {event}")

    updated_answer = {
        'content': get_follow_up(event['query'])
    }

    r = requests.post(
        FOLLOW_UP_URL.format(event['application_id'], event['token']),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(updated_answer)
    )
    
    if r.status_code == 200:
        logger.debug('Sent message successfully')
    else:
        logger.debug(f"Discord responded with status code {r.status_code}: {r.text}")

    return {}