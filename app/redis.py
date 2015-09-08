from __future__ import absolute_import
from __future__ import unicode_literals

from abc import ABCMeta
from six import with_metaclass

from app import r as redis
from app.util import camel_to_underscore

import collections

# String converter
String = lambda bytes: bytes.decode('utf-8')


class Key:
    """Key defines an the configuration of an attribute for a model

    It provides a converter to parse the value from redis
    """
    def __init__(self, converter=String, primary=False, index=False, prefix=''):
        self.__converter__ = converter
        self.primary = primary
        self.index = index
        self.prefix = prefix

    def __call__(self, value):
        """Convert the string using the specified converter"""
        return self.__converter__(value)


class Index(collections.MutableMapping):
    """Defines an index on redis with an optional relationship

    An index basically behaves as a dictionary, where all dictionary
    operations apply
    """
    def __init__(self, prefix='', relationship=None):
        self.__prefix__ = prefix
        self.__relationship__ = relationship

    def __getitem__(self, key):
        value = redis.get(self.__keytransform__(key))

        if value and self.__relationship__:
            # Create an object of the specified relationship
            return self.__relationship__(value.decode())

        return value

    def __setitem__(self, key, value):
        if isinstance(value, Model):
            # If the value is a model , use the id
            value = value.id

        return redis.set(self.__keytransform__(key), value)

    def __keytransform__(self, key):
        if not key.startswith(self.__prefix__):
            return self.__prefix__ + key

        return key

    def __delitem__(self, key):
        return redis.delete(self.__keytransform__(key))

    def __iter__(self):
        return iter(map(lambda s: s.decode('utf-8')[len(self.__prefix__):], redis.keys(self.__prefix__ + '*')))

    def __len__(self):
        return len(redis.keys(self.__prefix__ + '*'))

    def __contains__(self, key):
        return redis.exists(self.__keytransform__(key))

    def rename(self, old, new):
        return redis.rename(self.__keytransform__(old), self.__keytransform__(new))

    def deleteall(self):
        keys = redis.keys(self.__prefix__ + '*')
        if len(keys) > 0:
            return redis.delete(*keys)

        return 0


class ModelType(type):
    pass


class ModelMeta(ModelType, ABCMeta):
    def __new__(mcl, name, bases, attrs):
        cls = super(ModelMeta, mcl).__new__(mcl, name, bases, attrs)

        # Get the model configuration
        cls.__keys__ = {}
        cls.__indexes__ = {}
        cls.__prefix__ = cls.__prefix__ if hasattr(cls, '__prefix__') else None
        cls.__primary__ = None
        for name in cls.__dict__:
            if isinstance(cls.__dict__[name], Key):
                key = cls.__dict__[name]
                cls.__keys__[name] = key

                if key.primary:
                    if cls.__primary__ is not None:
                        raise AttributeError("Only one primary index can be defined")

                    # Use 'modelname:' as prefix by default
                    cls.__prefix__ = key.prefix if key.prefix else camel_to_underscore(cls.__name__) + ':'
                    cls.__primary__ = name

                elif key.index:
                    index = Index(prefix=key.prefix if key.prefix else camel_to_underscore(cls.__name__) + '_' + name + ':', relationship=cls)
                    cls.__indexes__[name] = index

        return cls


class Model(with_metaclass(ModelMeta, collections.MutableMapping)):
    """Defines a basic model for data storage using HASH inside
    redis.

    Implementing classes must define either a __prefix__ attribute to identify the id
    of the model, or a key with primary=True defined, which will be used as id for the model
    """

    def __init__(self, id):
        if not hasattr(self, '__prefix__'):
            raise AttributeError("Models must define the attribute: __prefix__ or define one of the model keys as primary")

        value = id
        if not id.startswith(self.__prefix__):
            id = self.__prefix__ + id
        else:
            value = id[len(self.__prefix__):]

        self.id = id

        # If primary is set, then we need to set the value of the
        # appropriate key
        if self.__primary__:
            self.__setitem__(self.__primary__, value)

    def __getattribute__(self, name):
        try:
            attr = super(Model, self).__getattribute__(name)
            if isinstance(attr, Key):
                # If the attribute is a key. return the key value instead
                # of the key object
                return self.__getitem__(name)
            return attr
        except AttributeError:
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
                isinstance(cls.__dict__[name], property):
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

        if key in self.__keys__:
            # Use the converter specified by the
            # key configuration
            return self.__keys__[key](value)

        # Try to parse numeric types
        parsers = [int, float]
        for parse in parsers:
            try:
                return parse(value)
            except ValueError:
                pass

        return value.decode('utf-8')

    def __setitem__(self, key, value):
        if self.__primary__ and key == self.__primary__ and \
                self.__contains__(key) and self.__getitem__(key) != value:
            raise AttributeError("The item '%s' of model %s has been set as primary, thus it cannot be changed" % (key, self.__class__.__name__))

        if key in self.__indexes__:
            oldvalue = self.__getitem__(key)
            # If the value has already used as a key
            if oldvalue and oldvalue != value and \
                    oldvalue in self.__indexes__[key] and \
                    self.__indexes__[key][oldvalue] == self:
                # Use rename to update the index
                self.__indexes__[key].rename(oldvalue, value)
            else:
                # Otherwise update the index
                self.__indexes__[key][value] = self

        return redis.hset(self.id, self.__keytransform__(key), value)

    def __delitem__(self, key):
        if key in self.__indexes__:
            oldvalue = self.__getitem__(key)
            # If the key is an index, delete the index
            if oldvalue:
                del self.__indexes__[key][oldvalue]

        redis.hdel(self.id, self.__keytransform__(key))

    def __iter__(self):
        return iter(redis.hkeys(self.id))

    def __len__(self):
        return redis.hlen(self.id)

    def __keytransform__(self, key):
        return key

    def __repr__(self):
        return repr(redis.hgetall(self.id))

    def __eq__(self, other):
        if not isinstance(other, Model):
            return False

        return self.id == other.id

    def __contains__(self, key):
        return redis.hexists(self.id, self.__keytransform__(key))

    def incrby(self, key, amount=1):
        """Increment the provided key in the dictionary by the specified amount"""
        redis.hincrby(self.id, self.__keytransform__(key), amount)

    def delete(self):
        """Delete the entity from the database"""
        # Delete the indexes
        for key in self.__indexes__:
            oldvalue = self.__getitem__(key)
            # If the key is an index, delete the index
            if oldvalue:
                del self.__indexes__[key][oldvalue]

        return redis.delete(self.id)

    @classmethod
    def exists(cls, id):
        if not hasattr(cls, '__prefix__'):
            raise AttributeError("Models must define the attribute: __prefix__ or define one of the model keys as primary")

        if not id.startswith(cls.__prefix__):
            id = cls.__prefix__ + id

        return redis.exists(id)

    @classmethod
    def findBy(cls, key, value):
        if key == cls.__primary__ and cls.exists(value):
            return cls(value)

        if key not in cls.__indexes__:
            raise AttributeError("No index has been defined for key '%s' in model %s" % (key, cls.__name__))

        return cls.__indexes__[key][value]

    @classmethod
    def all(cls, *args, **kwargs):
        """Return an iterator over the objects matching the model in the database

        It performs the query by calling redis.keys() using the defined prefix.
        If extra arguments are given, they are passed to the contructor of the model.
        """
        if not hasattr(cls, '__prefix__'):
            raise AttributeError("Models must define the attribute: __prefix__ or define one of the model keys as primary")

        keys = redis.keys(cls.__prefix__ + '*')
        for key in keys:
            yield cls(key.decode(), *args, **kwargs)

    @classmethod
    def deleteall(cls):
        if not hasattr(cls, '__prefix__'):
            raise AttributeError("Models must define the attribute: __prefix__ or define one of the model keys as primary")

        keys = redis.keys(cls.__prefix__ + '*')
        if len(keys) > 0:
            for key in cls.__indexes__:
                cls.__indexes__[key].deleteall()

            return redis.delete(*keys)

        return 0
