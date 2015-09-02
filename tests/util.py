from __future__ import absolute_import
from __future__ import unicode_literals


from flask import json
from .base import BaseTestCase
from app.util import parse_project_name_from_repo_url

class UtilTestCase(BaseTestCase):
    def test_parse_project_name(self):
        project = parse_project_name_from_repo_url("https://github.com/flalanne/gitbot/issues/1", "issues")
        assert project.get('namespace') == 'flalanne'
        assert project.get('name') == 'gitbot'
        assert project.get('url') == 'https://github.com/flalanne/gitbot'

        project = parse_project_name_from_repo_url("https://github.com/flalanne/gitbot", "issues")
        assert project.get('namespace') == 'flalanne'
        assert project.get('name') == 'gitbot'
        assert project.get('url') == 'https://github.com/flalanne/gitbot'

        project = parse_project_name_from_repo_url("https://github.com/flalanne/gitbot")
        assert project.get('namespace') == 'flalanne'
        assert project.get('name') == 'gitbot'
        assert project.get('url') == 'https://github.com/flalanne/gitbot'

        project = parse_project_name_from_repo_url("https://mine.gitlab.com/repo")
        assert project.get('name') == 'repo'
        assert project.get('url') == 'https://mine.gitlab.com/repo'

        project = parse_project_name_from_repo_url("https://mine.gitlab.com/myrepo/issues/1", "issues")
        assert project.get('name') == 'myrepo'
        assert project.get('url') == 'https://mine.gitlab.com/myrepo'
