from __future__ import absolute_import
from __future__ import unicode_literals


class Config(object):
    DEBUG = False
    TESTING = False

    # Host for the redis server
    REDIS = 'redis'

    # Do not push this to a public repo
    SLACK_DEFAULT_CHANNEL = '#general'
    SLACK_DEVELOPERS_CHANNEL = '#developers'

    # Define the application directory
    import os
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Log file (the directory must exist)
    APPLICATION_LOG = os.path.join(BASE_DIR, 'log', 'application.log')

    # Secret key for flask sessions and CSRF protection
    SECRET_KEY = "secret key that you need to change, seriously!"

class ProductionConfig(Config):
    SLACK_TOKEN = 'here you put the slack token'

    # Gitlab hook url
    GITLAB_HOOK = '/hooks/bWxNGVQij55cCZigeKDlXf9P6L14bKc4AhdPmPL5mEc='

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True


# Default configuration
default = DevelopmentConfig
