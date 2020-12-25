from slack import WebClient
from django.conf import settings
import logging
logger = logging.Logger(__name__)


def send_msg_with_the_menu(message):
    """
    Send Message reminder to all slack user with the day menu
    :param message: the message to send
    :return: True if there's no error in the sending process else False
    """
    try:
        slack_client = WebClient(settings.SLACK_BOT_TOKEN)
        slack_client.chat_postMessage(channel=settings.CHANNEL_ID, text=message)
        logger.info("Slack reminder sent")
        return True
    except Exception as e:
        logger.error("Error in sending slack reminder %s" % e)
        return False


def invite_to_channel(email):
    """
    send invite to the workspace
    :param email: the email of chilean employee to send invite
    :return: True if invitation sent else False
    """
    try:
        slack_client = WebClient(settings.SLACK_BOT_TOKEN)
        info = slack_client.team_info()
        channels_list = slack_client.conversations_list()
        for channel in channels_list.data.get('channels', {}):
            if channel.get('name') == settings.CHANNEL_ID:
                channel_id = channel.get('id')
        # TODO verify the function
        slack_client.admin_users_invite(team_id=info.data.get('team', {}).get('id'),
                                        email=email,
                                        channel_ids=[channel_id, ])
        return True
    except:
        return False