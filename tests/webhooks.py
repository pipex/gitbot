from __future__ import absolute_import
from __future__ import unicode_literals

from flask import json
from .base import BaseTestCase
from app import webhooks

from werkzeug.exceptions import NotImplemented

hook1 = "/tests/gwzXzRrXZyk8fesADQAVe6WwI/NDiOMUGEoVmUi48ro"
hook2 = "/tests/RkcvQihDxtyWhSP/FoGdO4o4Tm4QhE3Z0NpTpOVLWIo"
hook3 = "/tests/lfuO4ZcfPFMFZRWQhHVl8EXgMtGVZlU4eCuL69jbwj8"
hook4 = "/tests/a6cyEl8q5e81+R6WohDX6N3BXqIpMyImMnN4Ub4nEMk"
hook5 = "/tests/kVvVA4ZURRCnCzcYesHiZkpjga3Rq5FkbRA7xoel8MU"

@webhooks.hook(hook1)
class Hook1:
    pass

@webhooks.hook(hook2)
class Hook2:
    def event(self, request):
        return 'some_event'

@webhooks.hook(hook3)
class Hook3:
    def event(self, request):
        return 'some_event'

    def some_event(self, data):
        return json.dumps(data)


@webhooks.hook(hook4, handler='gitlab')
class Hook4:
    def commit_comment(self, data):
        return 'commit_comment'

    def issue_comment(self, data):
        return 'issue_comment'

    def merge_request_comment(self, data):
        return 'merge_request_comment'

    def snippet_comment(self, data):
        return 'snippet_comment'

class WebHooksTestCase(BaseTestCase):
    def test_event_method_not_implemented(self):
        try:
            self.app.post(hook1, follow_redirects=True, content_type='application/json')
            assert False
        except NotImplementedError:
            assert True

    def test_event_handler_not_implemented(self):
        rv = self.app.post(hook2, follow_redirects=True, content_type='application/json')
        assert rv.status_code == 501

    def test_event_called(self):
        data = json.dumps(dict(one=1, two=2))
        rv = self.app.post(hook3, follow_redirects=True, data=data, content_type='application/json')
        assert rv.status_code == 200
        assert rv.data.decode('utf-8') == data


class GitlabWebHooksTestCase(BaseTestCase):
    def test_event_without_header(self):
        rv = self.app.post(hook4, follow_redirects=True, content_type='application/json')
        assert rv.status_code == 400

    def test_event_with_wrong_header(self):
        rv = self.app.post(hook4, follow_redirects=True, content_type='application/json', headers={'X-Gitlab-Event': 'Some header'})
        assert rv.status_code == 501

    def test_event_with_unimplemented_method(self):
        rv = self.app.post(hook4, follow_redirects=True, content_type='application/json', headers={'X-Gitlab-Event': 'Issue Hook'})
        assert rv.status_code == 501

    def test_event_with_comment_note(self):
        rv = self.app.post(hook4, follow_redirects=True, content_type='application/json', data=json.dumps(dict(commit={'id': '123'})), headers={'X-Gitlab-Event': 'Note Hook'})
        assert rv.status_code == 200
        assert rv.data.decode('utf-8') == 'commit_comment'

    def test_event_with_issue_note(self):
        rv = self.app.post(hook4, follow_redirects=True, content_type='application/json', data=json.dumps(dict(issue={'id': '123'})), headers={'X-Gitlab-Event': 'Note Hook'})
        assert rv.status_code == 200
        assert rv.data.decode('utf-8') == 'issue_comment'

    def test_event_with_merge_request_note(self):
        rv = self.app.post(hook4, follow_redirects=True, content_type='application/json', data=json.dumps(dict(merge_request={'id': '123'})), headers={'X-Gitlab-Event': 'Note Hook'})
        assert rv.status_code == 200
        assert rv.data.decode('utf-8') == 'merge_request_comment'

    def test_event_with_snippet_note(self):
        rv = self.app.post(hook4, follow_redirects=True, content_type='application/json', data=json.dumps(dict(snippet={'id': '123'})), headers={'X-Gitlab-Event': 'Note Hook'})
        assert rv.status_code == 200
        assert rv.data.decode('utf-8') == 'snippet_comment'
