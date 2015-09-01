from __future__ import absolute_import
from __future__ import unicode_literals

from flask import json
from .base import BaseTestCase

class GitlabTestCase(BaseTestCase):
    def test_issues_hook_without_namespace(self):
        data = {
          "object_kind": "issue",
          "user": {
            "name": "Administrator",
            "username": "root",
            "avatar_url": "http://www.gravatar.com/avatar/e64c7d89f26bd1972efa854d13d7dd61?s=40\u0026d=identicon"
          },
          "object_attributes": {
            "id": 301,
            "title": "New API: create/update/delete file",
            "assignee_id": 51,
            "author_id": 51,
            "project_id": 14,
            "created_at": "2013-12-03T17:15:43Z",
            "updated_at": "2013-12-03T17:15:43Z",
            "position": 0,
            "branch_name": None,
            "description": "Create new API for manipulations with repository",
            "milestone_id": None,
            "state": "opened",
            "iid": 23,
            "url": "http://example.com/diaspora/issues/23",
            "action": "siopen"
          }
        }

        rv = self.app.post('/hooks/gitlab', follow_redirects=True,
                           data=json.dumps(data), content_type='application/json',
                           headers={'X-Gitlab-Event': 'Issue Hook'})


        assert rv.status_code == 200
        assert rv.data == """Administrator opened <http://example.com/diaspora/issues/23|issue #23> in <http://example.com/diaspora/issues|issues>: *New API: create/update/delete file*

> Create new API for manipulations with repository"""

    def test_issues_hook_with_namespace(self):
        data = {
            "object_attributes": {
                "action": "close",
                "assignee_id": 3,
                "author_id": 3,
                "branch_name": None,
                "created_at": "2015-08-29 21:59:03 UTC",
                "description": "This is an issue",
                "id": 54,
                "iid": 1,
                "milestone_id": None,
                "position": 0,
                "project_id": 83,
                "state": "closed",
                "title": "Created issue",
                "updated_at": "2015-08-29 22:30:31 UTC",
                "url": "http://git.niclabs.cl/flalanne/test-project/issues/1"
            },
            "object_kind": "issue",
            "user": {
                "avatar_url": "http://git.niclabs.cl/uploads/user/avatar/3/me.jpg",
                "name": "Felipe Lalanne",
                "username": "flalanne"
            }
        }

        rv = self.app.post('/hooks/gitlab', follow_redirects=True,
                           data=json.dumps(data), content_type='application/json',
                           headers={'X-Gitlab-Event': 'Issue Hook'})

        assert rv.status_code == 200
        assert rv.data == """<@flalanne> closed <http://git.niclabs.cl/flalanne/test-project/issues/1|issue #1> in <http://git.niclabs.cl/flalanne/test-project|test-project>: *Created issue*

> This is an issue"""
