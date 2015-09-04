from app import redis

import collections

class RedisOperationNotAllowedException(Exception):
    pass

class RedisModel(collections.MutableMapping):
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
        if name == 'id':
            if name in self.__dict__:
                # Cannot change id
                raise RedisOperationNotAllowedException("The model id cannot be changed")
            else:
                self.__dict__[name] = value

        self.__setitem__(name, value)

    def __getitem__(self, key):
        return redis.hget(self.id, self.__keytransform__(key))

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

    def incrby(self, key, amount=1):
        """Increment the provided key in the dictionary by the specified amount"""
        redis.hincrby(self.id, self.__keytransform__(key), amount)

    def delete(self):
        """Delete the entity from the database"""
        return redis.delete(self.id)

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
            yield cls(key, *args, **kwargs)

    @classmethod
    def deleteall(cls):
        if not hasattr(cls, '__prefix__'):
            raise AttributeError("Inheriting classes must define the attribute: __prefix__")

        return redis.delete(*redis.keys(cls.__prefix__+'*'))
