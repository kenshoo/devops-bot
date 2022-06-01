import os
import ssl
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from helper import logger

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
slack_token = os.environ.get("SLACK_BOT_TOKEN")
slack_client = WebClient(token=slack_token, ssl=ssl_context)


def get_email_from_slack(user_id):
    try:
        result = slack_client.users_info(user=user_id)
        return result.get("user").get("profile").get("email")
    except SlackApiError as e:
        logger.error("Couldn't get slack user's email: ", e)
        return None


def post_in_slack(user_id, message, blocks=None):
    try:
        # Call the chat.postMessage method using the WebClient
        if blocks is not None:
            slack_client.chat_postMessage(
                channel=user_id, token=slack_token, text=message, blocks=blocks
            )

        else:
            slack_client.chat_postMessage(
                channel=user_id, token=slack_token, text=message
            )

    except SlackApiError as e:
        logger.error(f"Error posting message: {e}")
