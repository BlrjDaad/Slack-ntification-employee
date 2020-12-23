
from slack import WebClient
from django.conf import settings


def send_msg_with_the_menu(message):
    slack_client = WebClient(settings.SLACK_BOT_TOKEN)
    slack_client.chat_postMessage(channel=settings.CHANNEL_ID, text=message)
