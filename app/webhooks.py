from __future__ import absolute_import
from __future__ import unicode_literals

from flask.views import MethodView
from flask import request
from .util import camel_to_underscore

from werkzeug.exceptions import NotImplemented
from logging import getLogger

import six

class WebHook(MethodView):
    def __init__(self, logger=None):
        self.logger = logger if logger else getLogger('webhooks')

    def event(self, request):
        """Returns the event name from the request information.
        """
        raise NotImplementedError('Subclasses must implement the event method.')

    def post(self):
        event = self.event(request)

        if not hasattr(self, event):
            raise NotImplemented('No method implemented for event %s.' % event)

        # Get a dict of POSTed data
        data = {k: d[k] for d in [request.json, request.form, request.args] for k in six.iterkeys(d or {})}

        self.logger.debug('Received %s event with the following data:\n %s' % (event, repr(data)))

        # Call the method with the json as parameter
        return getattr(self, event)(data)


class WebHooks:
    """Provides methods to define webhooks for a flask app"""

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.handlers = {}

    def add_handler(self, name, cls):
        """Set a webhook base class to handle requests for a specified type.

        Example:

        ```
        app = Flask(__name__)

        webhooks = WebHooks(app)
        webhooks.add_handler('github', GitHubWebHook)

        @webhooks.hook('/url/for/hook', handler='gitlab')
        class MyHook
            def issues(self, data):
                pass

            def commit_comment(self, data):
                pass
        ```
        """
        self.handlers[name] = cls

    def hook(self, prefix, handler=None):
        """Decorator for creating a webhook from a generic class

        If a handler is defined, it will try to get the handler from the list of defined
        handlers, otherwise it will default to the WebHook handler

        @webhooks.hook('/url/for/hook', handler='github')
        class MyHook
            def issues(self, data):
                pass

            def commit_comment(self, data):
                pass
        """
        def wrapper(cls):
            # Save the original init
            clsinit = getattr(cls, '__init__', lambda self: None)

            basecls = self.handlers.get(handler, self.app.config.get('WEBHOOKS_DEFAULT_HANDLER', WebHook))

            # Dirty trick, make the class belong to the type restful.Resource
            cls = type(cls.__name__, (basecls,), dict(cls.__dict__))

            # Save this instance in another class to use inside the method
            hook = self

            def __init__(self, *args, **kwargs):
                # Call Resource constructor
                super(cls, self).__init__(logger=hook.app.logger)

                # Initialize the instance
                clsinit(self, *args, **kwargs)

            cls.__init__ = __init__

            # Add the resource to the app
            self.app.add_url_rule(prefix, view_func=cls.as_view(camel_to_underscore(cls.__name__)))

            return cls

        return wrapper
