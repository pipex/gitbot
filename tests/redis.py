from __future__ import absolute_import
from __future__ import unicode_literals

from .base import BaseTestCase
from app import redis

class Entity(redis.Model):
    __prefix__ = 'entity:'

class RedisModelTestCase(BaseTestCase):
    def tearDown(self):
        Entity.deleteall()

    def test_model_operations(self):
        entity = Entity('one')

        entity['name'] = 'First entity'
        entity['data'] = 'ONE'
        assert entity['name'] == entity.name
        assert entity['data'] == entity.data

        entity.name = "First entity NEW"
        assert entity['name'] == entity.name

        newentity = Entity('entity:two')
        newentity['name'] = 'Second entity'
        newentity['data'] = 'SECOND'

        assert newentity['name'] == newentity.name
        assert newentity['data'] == newentity.data

        first = False
        second = False
        for e in Entity.all():
            if e.name == entity.name:
                first = True
            if e.name == newentity.name:
                second = True

        assert first
        assert second

        entity.delete()
        assert entity.name is None

        try:
            newentity.id = "three"
            assert False
        except AttributeError:
            assert True
