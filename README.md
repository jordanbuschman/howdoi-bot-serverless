# howdoi-bot

Ever have an existential question that you _need_ to know the answer to? Howdoi-bot is a serverless Discord bot that queries Yahoo Answers and gives you the best result. Included is the howdoi-bot code, and configuration for packaging/deploying the service via Cloudformation.

## Requirements

- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [Docker desktop](https://www.docker.com/products/docker-desktop)
- An AWS account

## Codebase

- `template.yml`: defines the project, including a gateway, 2 lambda functions, log groups, and IAM roles.
- `bin/register_command.sh`: For registering your slash command with Discord the first time you set up the project.
- `bin/setup.sh`:
  - Creates the `/build` directory
  - Installs dependencies in Amazon Linux using Docker, and creates a .zip of the dependencies
  - Takes all the code in `/src` and creates a second .zip
- `src/input.py`: Contains the lambda handler that Discord talks to.
- `src/response.py`: Contains the lambda handler that actually fetches your response (as this can take longer than Discord allows slash commands to take).

## First Time Setup

1. Create a new Discord application and bot on the [Discord developer portal](https://discord.com/developers/applications). Note the bot's public key and bot token.
2. Install and zip python package requirements with `bash bin/setup.sh`.
3. Create a bucket in S3 to store your assets.
4. Run the following to package your template:

    ```sh
    sam package \
        --s3-bucket <YOUR_S3_BUCKET_HERE> \
        --template-file template.yml \
        --output-template-file output.yml
    ```

5. Run the following command to deploy your stack via Cloudformation:

    ```sh
    sam deploy \
        --template-file output.yml \
        --stack-name howdoi-bot \
        --capabilities CAPABILITY_IAM \
        --parameter-overrides \
            DiscordPublicKey=<YOUR_PUBLIC_KEY_HERE> \
    ```

6. Once your stack has been created, [check your API](https://console.aws.amazon.com/apigateway). Copy the `Invoke URL`.
7. On your Discord application page, paste the invoke URL in the `Interractions Endpoint URL` box, and press 'Save'.
8. Register your slash command. You can run the curl command in `bin/register_command.sh` after adding your application ID/bot token (see further reading for more info).
9. Invite your discord bot to your room. Enjoy the shitposts!

## Pushing Out Changes

Whenever you update the code, you can do steps 2, 4, and 5 to update your Cloudformation stack. In step 4, You may need to pass in the `--force-upload` flag for your assets to replace the old ones in S3.

## Further Reading

- <https://oozio.medium.com/serverless-discord-bot-55f95f26f743> - Medium article detailing a manual setup similar to this one
- <https://discord.com/developers/docs/interactions/slash-commands#registering-a-command> - Discord API: Registering a slash command
