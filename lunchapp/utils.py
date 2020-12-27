from django.conf import settings
from slack import WebClient

import logging
logger = logging.Logger(__name__)


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