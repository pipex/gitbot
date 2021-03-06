from __future__ import absolute_import
from __future__ import unicode_literals

from app import app, webhooks, slack
from app.models import User, Channel
from app.util import parse_project_name_from_repo_url
from flask import json, make_response, render_template
from functools import partial

default_response = partial(make_response, '', 200)


@app.template_filter('render_slack_user')
def render_slack_user(slack_user):
    if isinstance(slack_user, User):
        return '<%s>' % slack_user.id

    return slack_user['full_name']


@webhooks.hook(
    app.config.get('GITLAB_HOOK', '/hooks/gitlab'),
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
        namespace_user = User.findBy('gitlab_name', project.get('namespace')) if project.get('namespace') else None
        if namespace_user:
            # If the namespace is a slack user, send data directly to the user channel
            channel = '@' + namespace_user.name

        for name in names:
            if channel:
                break
            channel = name if Channel.exists(name) else None

        # Get the user info
        gitlab_user = data.get('user')

        # Check if the username matches slack username
        user = {}
        user['full_name'] = gitlab_user.get('name')
        slack_user = User.findBy('gitlab_name', gitlab_user.get('username'))
        if slack_user:
            user = slack_user

        # Generate the response text
        message = render_template('issue.txt', user=user, project=project, issue=issue)

        if not app.config.get('TESTING', False):
            # Send message to slack
            slack.chat.post_message(channel, message)
        else:
            # Return message to check in testing
            return message

        return default_response()

    def push(self, data):
        # Read commit list to update commit count for user
        if not self.check_object_kind(data, 'tag_push'):
            # This should not happen
            return default_response()

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
        if project.get('namespace') and User.findBy('gitlab_name', project.get('namespace')):
            # If the namespace is a slack user, we probably don't need to notify of a new
            # tag push
            return default_response()

        # Get the tag reference
        reference = data.get('ref')

        # Usually the reference is given by refs/tags/<tagname>
        refs, name, tag = reference.split('/')
        message = data.get('message')

        user = {}
        user['full_name'] = data.get('user_name')
        if data.get('user_email'):
            # Get the user by email. Assume that the same email is used for
            # Gitlab and slack
            slack_user = User.findBy('email', data.get('user_email'))
            if slack_user:
                user = slack_user

        team = project.get('namespace', project.get('name'))

        # Generate the response text
        response = render_template('tag.txt', user=user, project=project, message=message, team=team, tag=tag)

        if not app.config.get('TESTING', False):
            # Send message to slack
            slack.chat.post_message(channel, response)
        else:
            # slack.chat.post_message('#slack-test', response)
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
