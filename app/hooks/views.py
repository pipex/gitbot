from __future__ import absolute_import
from __future__ import unicode_literals

from app import app, webhooks

@webhooks.hook(
    app.config.get('GITLAB_HOOK','/hooks/gitlab'),
    handler='gitlab')
class Gitlab:
    def issue(self, data):
        # if the repository belongs to a group check if a channel with the same
        # name (lowercased and hyphened) exists
        # Check if a channel with the same repository name exists

        # If the channel exists post to that channel

        # If not post to general or other defined by configuration

        # publish the issue to the found channel including the Title, Message
        # and the creator and responsible if defined
        pass

    def push(self, data):
        # Read commit list to update commit count for user
        pass

    def tag_push(self, data):
        # Publish news of the new version of the repo in general
        pass

    def merge_request(self, data):
        # Notify in the channel
        pass

    def commit_comment(self, data):
        # Notify comment and receiver in the channel
        pass

    def issue_comment(self, data):
        # Notify comment and receiver in the channel
        pass

    def merge_request_comment(self, data):
        # Notify comment and receiver in the channel
        pass

    def snippet_comment(self, data):
        # Do nothing for now
        pass
