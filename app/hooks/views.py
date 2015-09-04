from __future__ import absolute_import
from __future__ import unicode_literals

from app import app, webhooks, slack
from app.models import get_channel_id, get_user_id
from app.util import parse_project_name_from_repo_url
from flask import json, make_response, render_template
from functools import partial

default_response = partial(make_response, '', 200)

@webhooks.hook(
    app.config.get('GITLAB_HOOK','/hooks/gitlab'),
    handler='gitlab')
class Gitlab:
    def check_object_kind(self, obj, expected):
        object_kind = obj.get('object_kind', None)
        if object_kind != expected:
            # This should not happen
            app.logger.error("Received object_kind '%s' when expecting '%s'" % (object_kind, expected))
            return False

        return True

    def issue(self, data):
        if not self.check_object_kind(data, 'issue'):
            # This should not happen
            return default_response()

        # Get the issue object
        issue = data.get('object_attributes')

        # Get the project data from the url, since there is no 'repository' provided
        project = parse_project_name_from_repo_url(issue.get('url'), resource='issues')

        # If the project has a namespace, check that the namespace exists in slack
        # Otherwise try to find the channel matching the project name
        # Finally check SLACK_DEVELOPERS_CHANNEL or #general
        names = [i for i in [project.get('namespace'),
                             project.get('name'),
                             app.config.get('SLACK_DEVELOPERS_CHANNEL'),
                             '#general'] if i is not None]

        channel = None
        if  project.get('namespace') and get_user_id(project.get('namespace')):
            # If the namespace is a slack user, send data directly to the user channel
            channel = '@' + project.get('namespace')

        for name in names:
            if channel: break
            channel = name if get_channel_id(name) else None

        # Get the user info
        user = data.get('user')

        # Check if the username matches slack username
        username = user.get('name')
        if get_user_id(user.get('username')):
            username = "<@%s>" % user.get('username')

        # Generate the response text
        message = render_template('issue.txt', username=username, project=project, issue=issue)

        if not app.config.get('TESTING', False):
            # Send message to slack
            slack.chat.post_message(channel, message)
        else:
            # Return message to check in testing
            return message

        return default_response()

    def push(self, data):
        # Read commit list to update commit count for user
        pass

    def tag_push(self, data):
        # Publish news of the new version of the repo in general
        if not self.check_object_kind(data, 'tag_push'):
            # This should not happen
            return default_response()

        # Get the project data
        repository = data.get('repository')
        project = parse_project_name_from_repo_url(repository.get('homepage'))

        # For now all tag messages go to #general to notify the whole team of the
        # new version
        channel = '#general'
        if  project.get('namespace') and get_user_id(project.get('namespace')):
            # If the namespace is a slack user, we probably don't need to notify of a new
            # tag push
            return default_response()

        # Get the tag reference
        reference = data.get('ref')

        # Usually the reference is given by refs/tags/<tagname>
        refs, name, tag = reference.split('/')
        message = data.get('message')

        # Gitlab is not very consitent with its responses
        # Check if the user part of the email matches the username in slack
        # TODO: create an association between email and slack username?
        username = data.get('user_name')
        if data.get('user_email'):
            u, d = data.get('user_email').split('@')
            if get_user_id(u):
                username = "<@%s>" % u

        team = project.get('namespace', project.get('name'))

        # Generate the response text
        response = render_template('tag.txt', username=username, project=project, message=message, team=team, tag=tag)

        if not app.config.get('TESTING', False):
            # Send message to slack
            slack.chat.post_message(channel, response)
        else:
            #slack.chat.post_message('#slack-test', response)
            # Return message to check in testing
            return response

        return default_response()


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
