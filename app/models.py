from app import slack, redis, app

from app.redis import RedisModel

class Channel(RedisModel):
    __prefix__ = '#'

    @staticmethod
    def load_from_slack():
        """Update channel list from slack"""
        slack_response = slack.channels.list()

        if not slack_response.successful:
            app.logger.error('Error loading channel list. Server returned %s' % slack_response.error)
            return False

        # Add channel to list and save
        for channel in slack_response.body.get('channels', []):
            name = channel.get('name')

            entity = Channel(channel.get('name'))
            entity.slack_id = channel.get('id')

        return True


class User(RedisModel):
    __prefix__ = '@'

    @property
    def updated(self):
        if 'updated' in self:
            return datetime.strptime(self['updated'], "%Y-%m-%dT%H:%M:%S.%fZ")

        return None

    @updated.setter
    def updated(self, value):
        self['updated'] = datetime.strftime(value, "%Y-%m-%dT%H:%M:%S.%fZ")

    @staticmethod
    def load_from_slack(include_bots=False, include_deleted=False):
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

            entity = User(user.get('name'))
            entity.slack_id = user.get('id')

        return True

def load_data_from_slack():
    """Load data from slack.

    To be called on application start"""

    Channel.load_from_slack()
    User.load_from_slack()
