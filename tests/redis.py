from __future__ import absolute_import
from __future__ import unicode_literals

from .base import BaseTestCase
from app import redis


class Entity(redis.Model):
    __prefix__ = 'entity:'


class OtherEntity(redis.Model):
    primary = redis.Key(primary=True)


class ThirdEntity(redis.Model):
    id = redis.Key(prefix='third:', primary=True)
    name = redis.Key(index=True)


class RedisModelTestCase(BaseTestCase):
    def tearDown(self):
        Entity.deleteall()
        OtherEntity.deleteall()
        ThirdEntity.deleteall()

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

    def test_other_model_operations(self):
        entity = OtherEntity('one')

        entity['name'] = 'First entity'
        entity['data'] = 'ONE'

        assert entity['name'] == entity.name
        assert entity['data'] == entity.data

        entity.name = "First entity NEW"
        assert entity['name'] == entity.name

        newentity = OtherEntity('other_entity:two')
        newentity['name'] = 'Second entity'
        newentity['data'] = 'SECOND'

        assert newentity['name'] == newentity.name
        assert newentity['data'] == newentity.data

        first = False
        second = False
        for e in OtherEntity.all():
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

        try:
            newentity['primary'] = 'other'
            assert False
        except AttributeError:
            assert True

    def test_third_model_operations(self):
        entity = ThirdEntity('one')

        entity['name'] = 'First entity'
        entity['data'] = 'ONE'

        assert entity['name'] == entity.name
        assert entity['data'] == entity.data

        entity.name = "First entity NEW"
        assert entity['name'] == entity.name

        newentity = ThirdEntity('two')
        newentity['name'] = 'Second entity'
        newentity['data'] = 'SECOND'

        assert newentity['name'] == newentity.name
        assert newentity['data'] == newentity.data

        assert ThirdEntity.findBy('name', 'Second entity').data == newentity.data

        first = False
        second = False
        for e in ThirdEntity.all():
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

        try:
            newentity['id'] = 'other'
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

        name_index = redis.Index(prefix='name:', relationship=Entity)
        name_index['First'] = one
        name_index['Second'] = two

        assert name_index['First'].name == one.name
        assert name_index['First'].data == one.data

        assert name_index['Second'].name != one.name
        assert name_index['Second'].name == two.name
        assert name_index['Second'].data == two.data

        first = False
        second = False
        for k in name_index:
            if k == one.name:
                first = True
            if k == two.name:
                second = True

        assert first
        assert second

        del name_index['First']
        assert 'First' not in name_index
        del name_index['Second']
