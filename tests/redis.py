from __future__ import absolute_import
from __future__ import unicode_literals

from .base import BaseTestCase
from app import redis


class Entity(redis.Model):
    __prefix__ = 'entity:'


class NameIndex(redis.Index):
    __prefix__ = 'name:'
    __relation__ = Entity


class RedisModelTestCase(BaseTestCase):
    def tearDown(self):
        Entity.deleteall()
        NameIndex.deleteall()

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

    def test_index_operations(self):
        one = Entity('one')
        one['name'] = 'First'
        one['data'] = 'Number one'

        two = Entity('two')
        two['name'] = 'Second'
        two['data'] = 'Number two'

        NameIndex('First').set(one)
        NameIndex('Second').set(two)

        assert NameIndex('First').get().name == one.name
        assert NameIndex('First').get().data == one.data

        assert NameIndex('Second').get().name != one.name
        assert NameIndex('Second').get().name == two.name
        assert NameIndex('Second').get().data == two.data

        first = False
        second = False
        for e in NameIndex.all():
            if e.key == one.name:
                first = True
            if e.key == two.name:
                second = True

        assert first
        assert second

        first = False
        second = False
        for k, e in NameIndex.items():
            if e.name == one.name:
                first = True
            if e.name == two.name:
                second = True

        assert first
        assert second

        NameIndex('First').delete()
        assert not NameIndex('First').get()
        assert not NameIndex.contains('First')
