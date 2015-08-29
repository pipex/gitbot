from __future__ import absolute_import
from __future__ import unicode_literals

from app import app
import unittest


class BaseTestCase(unittest.TestCase):
    __test__ = False

    def setUp(self):
        # Load testing configuration
        app.config.from_object('config.TestingConfig')
        self.app = app.test_client()

        # Initialize the request context
        app.test_request_context().push()
