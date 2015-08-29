from __future__ import absolute_import
from __future__ import unicode_literals


class Config(object):
    DEBUG = False
    TESTING = False

    # Host for the redis server
    REDIS = 'redis'

    # Define the application directory
    import os
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Log file (the directory must exist)
    APPLICATION_LOG = os.path.join(BASE_DIR, 'log', 'application.log')

    # Secret key for flask sessions and CSRF protection
    SECRET_KEY = "secret key that you need to change, seriously!"

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True


# Default configuration
default = DevelopmentConfig
