from app import slack, redis, app

def get_channels(force_update=False):
    channels = redis.get('channels')
    if not channels or force_update:
        update_channels()

    return redis.smembers('channels')

def get_channel_id(channel):
    """Get channel slack id."""
    if not channel.startswith('#'):
        channel = "#%s" % channel

    return redis.get(channel)

def get_user_id(username):
    """Get user slack id"""
    if not username.startswith('#'):
        username = "@%s" % username

    id = redis.get(username)
    if not id:
        # Update the list
        update_users()

        # Try again
        id = redis.get(username)

    return id


def update_channels():
    """Update channel list from slack"""
    slack_response = slack.channels.list()

    if not slack_response.successful:
        app.logger.error('Error loading channel list. Server returned %s' % slack_response.error)
        return False

    # Add channel to list and save
    for channel in slack_response.body.get('channels', []):
        name = '#%s' % channel.get('name')

        # Save the id of the channel
        redis.set(name, channel.get('id'))

        # Add the name to a channels set
        redis.sadd('channels', name)

    return True


def update_users(include_bots=False, include_deleted=False):
    """Update user list from slack"""
    slack_response = slack.users.list()

    if not slack_response.successful:
        app.logger.error('Error loading user list. Server returned %s' % slack_response.error)
        return False

    # Add channel to list and save
    for user in slack_response.body.get('members', []):
        if user.get('is_bot') and not include_bots:
            continue

        if user.get('deleted') and not include_deleted:
            continue

        name = '@%s' % user.get('name')

        # Save the id of the user
        redis.set(name, user.get('id'))

        # Add the name to a users set
        redis.sadd('users', name)

    return True


def load_data():
    """Load data from slack.

    To be called on application start"""

    update_channels()
    update_users()
