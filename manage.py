from __future__ import absolute_import
from __future__ import unicode_literals

from flask.ext.script import Manager
from app import app

manager = Manager(app)

if __name__ == '__main__':
    manager.run()
