from datetime import datetime

from app import slack, redis, app

class Channel(redis.Model):
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


class User(redis.Model):
    __prefix__ = '@'

    @property
    def commits_updated(self):
        if 'commits_updated' in self:
            return datetime.strptime(self['commits_updated'], "%Y-%m-%dT%H:%M:%S.%fZ")

        return None

    @commits_updated.setter
    def commits_updated(self, value):
        self['commits_updated'] = datetime.strftime(value, "%Y-%m-%dT%H:%M:%S.%fZ")

    @property
    def commits_average(self):
        if 'days' in self and self.days > 0:
            return self.commits_total / self.days

        return 0.0

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

            profile = user.get('profile')
            if profile:
                if profile.get('email'):
                    entity.email = profile.get('email')

                    # Create the index
                    EmailIndex(profile.get('email')).set(entity)

                if profile.get('first_name'):
                    entity.first_name = profile.get('first_name')

        return True

    def update_commits(self, commits=1):
        """Update the number of commits"""
        if not 'commits_updated' in self:
            # Start from 0
            self.commits_updated        = datetime.now()
            self.commits_in_last_day    = 0
            self.commits_in_last_week   = 0
            self.commits_in_last_month  = 0
            self.commits_in_last_year   = 0
            self.commits_total = 0
            self.days = 1

        # We will check the dates
        now = datetime.now()
        updated = self.commits_updated

        # Save the difference
        delta = now - updated

        # If more than one day has passed since last commit, reset daily commit count
        if delta.days > 0:
            self.commits_in_last_day = 0

            # And increase the number of days counting
            self.incrby('days', 1)

        # If the week has changed between commits, reset weekly commit count
        if abs(now.isocalendar()[1] - updated.isocalendar()[1]) > 0:
            # Week changed
            self.commits_in_last_week = 0

        # If the month changed, reset monthly commit count
        if abs(now.month - updated.month) > 0:
            self.commits_in_last_month = 0

        # If the year changed, reset yearly commit count
        if now.year - updated.year > 0:
            self.commits_in_last_week = 0 # In case there has been no activity in an exact year
            self.commits_in_last_month = 0
            self.commits_in_last_year = 0

        # Increase count. Use incrby for efficiency
        self.incrby('commits_in_last_day', commits)
        self.incrby('commits_in_last_week', commits)
        self.incrby('commits_in_last_month', commits)
        self.incrby('commits_in_last_year', commits)
        self.incrby('commits_total', commits)

        # Change update date
        self.commits_updated = now


class EmailIndex(redis.Index):
    __prefix__ = 'e-mail:'
    __relation__ = User


def load_data_from_slack():
    """Load data from slack.

    To be called on application start"""

    Channel.load_from_slack()
    User.load_from_slack()
