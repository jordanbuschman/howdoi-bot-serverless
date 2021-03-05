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
FOLLOW_UP_URL = 'https://discord.com/api/v8/webhooks/{}/{}'