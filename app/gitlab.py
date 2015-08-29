from __future__ import absolute_import
from __future__ import unicode_literals

from .webhooks import WebHook
from werkzeug.exceptions import BadRequest, NotImplemented

EVENTS = {
    'Push Hook': 'push',
    'Tag Push Hook': 'tag_push',
    'Issue Hook': 'issue',
    'Note Hook': 'note',
    'Merge Request Hook': 'merge_request'
}

class GitlabWebHook(WebHook):
    def event(self, request):
        gitlab_header = request.headers.get('X-Gitlab-Event', None)

        if not gitlab_header:
            raise BadRequest('Gitlab requests must provide a X-Gitlab-Event header')

        event = EVENTS.get(gitlab_header, None)
        if not event:
            raise NotImplemented('Header not understood %s' % gitlab_header)

        if event == 'note':
            if 'commit' in request.json:
                event = 'commit_comment'
            elif 'merge_request' in request.json:
                event = 'merge_request_comment'
            elif 'issue' in request.json:
                event = 'issue_comment'
            elif 'snippet' in request.json:
                event = 'snippet_comment'

        return event
