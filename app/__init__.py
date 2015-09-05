from __future__ import absolute_import
from __future__ import unicode_literals

# Import flask and template operators
from flask import Flask, request, render_template

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config.default')

# Configure webhooks
from .webhooks import WebHooks
webhooks = WebHooks(app)

from .gitlab import GitlabWebHook
webhooks.add_handler('gitlab', GitlabWebHook)

# Configure Slacker
from slacker import Slacker
slack = Slacker(app.config.get('SLACK_TOKEN'))


# Configure storage
from redis import Redis
r = Redis(app.config.get('REDIS'))

# Configure logging
import logging
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter

# Configure the application log
if app.config.get('APPLICATION_LOG', None):
    application_log_handler = TimedRotatingFileHandler(app.config.get('APPLICATION_LOG'), 'd', 7)
    application_log_handler.setLevel(logging.INFO)
    application_log_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(application_log_handler)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Import modules
from app.public import views as public_views
from app.hooks import views as hook_views

# Load data from slack
from app.models import load_data_from_slack

# Store some slack data locally
load_data_from_slack()
