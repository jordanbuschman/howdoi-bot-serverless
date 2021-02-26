curl -XPOST https://discord.com/api/v8/applications/APPLICATION_ID/commands \
    -H "Authorization: Bot BOT_TOKEN_HERE" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "howdoi",
        "description": "Ask a question and receive an answer",
        "options": [
            {
                "name": "question",
                "description": "Question to ask howdoi-bot",
                "type": 3,
                "required": true
            }
        ]
    }'