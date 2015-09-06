from __future__ import absolute_import
from __future__ import unicode_literals

from app import r as redis

import collections

class Model(collections.MutableMapping):
    """Defines a basic model for data storage using HASH inside
    redis.

    Implementing classes must define a __prefix__ attribute, to group keys of the
    defined model.
    """

    def __init__(self, id):
        if not hasattr(self, '__prefix__'):
            raise AttributeError("Inheriting classes must define the attribute: __prefix__")

        if not id.startswith(self.__prefix__):
            id = self.__prefix__ + id

        self.id = id

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __setattr__(self, name, value):
        """Set the attribute with the value given by 'value'

        It works by calling self.__setitem__ with a couple of exceptions
        if the attribute name is 'id', it can only be set if it has not been set
        before.

        If a property setter has been defined for the inheriting class with the same
        name as the key, then the method calls the property setter first.

        Property setters must take care to set the actual value using self[name] to
        avoid infinite loops
        """
        if name == 'id':
            if name in self.__dict__:
                # Cannot change id (TODO: use redis.rename()?)
                raise AttributeError("The model id cannot be changed")
            else:
                self.__dict__[name] = value
                return True

        cls = self.__class__

        # Check if there are property setter.
        # This only works if the property setter has the same name as the property
        if hasattr(cls, name) and \
            isinstance(models.User.updated, property):
            try:
                cls.__dict__[name].__set__(self, value)
                return True
            except AttributeError:
                # No setter with the same name defined
                pass

        return self.__setitem__(name, value)

    def __getitem__(self, key):
        value = redis.hget(self.id, self.__keytransform__(key))

        # If the value is none
        if not value:
            return None

        # Try to parse numeric types
        parsers = [int, float]
        for parse in parsers:
            try:
                return parse(value)
            except ValueError:
                pass

        return value.decode('utf-8')

    def __setitem__(self, key, value):
        return redis.hset(self.id, self.__keytransform__(key), value)

    def __delitem__(self, key):
        redis.hdel(self.id, self.__keytransform__(key))

    def __iter__(self):
        return iter(redis.hgetall(self.id))

    def __len__(self):
        return redis.hlen(self.id)

    def __keytransform__(self, key):
        return key

    def __repr__(self):
        return repr(redis.hgetall(self.id))

    def __contains__(self, key):
        return redis.hexists(self.id, self.__keytransform__(key))

    def incrby(self, key, amount=1):
        """Increment the provided key in the dictionary by the specified amount"""
        redis.hincrby(self.id, self.__keytransform__(key), amount)

    def delete(self):
        """Delete the entity from the database"""
        return redis.delete(self.id)

    @classmethod
    def exists(cls, id):
        if not hasattr(cls, '__prefix__'):
            raise AttributeError("Inheriting classes must define the attribute: __prefix__")

        if not id.startswith(cls.__prefix__):
            id = cls.__prefix__ + id

        return redis.exists(id)

    @classmethod
    def all(cls, *args, **kwargs):
        """Return an iterator over the objects matching the model in the database

        It performs the query by calling redis.keys() using the defined prefix.
        If extra arguments are given, they are passed to the contructor of the model.
        """
        if not hasattr(cls, '__prefix__'):
            raise AttributeError("Inheriting classes must define the attribute: __prefix__")

        keys = redis.keys(cls.__prefix__+'*')
        for key in keys:
            yield cls(key.decode(), *args, **kwargs)

    @classmethod
    def deleteall(cls):
        if not hasattr(cls, '__prefix__'):
            raise AttributeError("Inheriting classes must define the attribute: __prefix__")

        keys = redis.keys(cls.__prefix__+'*')
        if len(keys) > 0:
            return redis.delete(*keys)


class Index(object):
    def __init__(self, key):
        if not hasattr(self, '__prefix__'):
            raise AttributeError("Inheriting classes must define the attribute: __prefix__")

        id = key
        if not key.startswith(self.__prefix__):
            id = self.__prefix__ + key
        else:
            key = key[len(self.__prefix__):]

        self.id = id
        self.key = key

    def get(self):
        value = redis.get(self.id)

        if value and hasattr(self, '__relation__'):
            # Create an object of the specified
            value = self.__relation__(value.decode())

        return value

    def set(self, value):
        if hasattr(value, 'id'):
            # If the valueue has an id, use the id
            value = value.id

        return redis.set(self.id, value)

    def delete(self):
        return redis.delete(self.id)

    @classmethod
    def deleteall(cls):
        if not hasattr(cls, '__prefix__'):
            raise AttributeError("Inheriting classes must define the attribute: __prefix__")

        keys = redis.keys(cls.__prefix__+'*')
        if len(keys) > 0:
            return redis.delete(*keys)

    @classmethod
    def all(cls, *args, **kwargs):
        if not hasattr(cls, '__prefix__'):
            raise AttributeError("Inheriting classes must define the attribute: __prefix__")

        keys = redis.keys(cls.__prefix__+'*')
        for key in keys:
            yield cls(key.decode(), *args, **kwargs)

    @classmethod
    def items(cls, *args, **kwargs):
        """Yield the key,object pairs in the index"""
        for index in cls.all(*args, **kwargs):
            yield index.key, index.get()

    @classmethod
    def contains(cls, key):
        if not hasattr(cls, '__prefix__'):
            raise AttributeError("Inheriting classes must define the attribute: __prefix__")

        if not key.startswith(cls.__prefix__):
            key = cls.__prefix__ + key

        return redis.exists(key)
