from __future__ import absolute_import
from __future__ import unicode_literals

from app import app, webhooks

@webhooks.hook(
    app.config.get('GITLAB_HOOK','/hooks/gitlab'),
    handler='gitlab')
class Gitlab:
    def issue(self, data):
        pass

    def push(self, data):
        pass

    def tag_push(self, data):
        pass

    def merge_request(self, data):
        pass

    def commit_comment(self, data):
        pass

    def issue_comment(self, data):
        pass

    def merge_request_comment(self, data):
        pass

    def snippet_comment(self, data):
        pass
