from typing import Any

from pydantic import BaseModel


def get_base_type(obj):
    return obj.__mro__[-2]


def get_type_name(_type):
    return f"{_type.__module__}.{_type.__name__}"


class SerializationMethod:
    prop_decorator = property

    def __init__(self, _type, func: callable):
        self.type = _type
        self.func = func

    @prop_decorator
    def type_name(self):
        _type = self.type
        return get_type_name(_type)

    def __hash__(self):
        return hash(self.type_name)

    def serialize(self, _obj, state: dict = None):
        state = state or {}
        if isinstance(_obj, self.type):
            return self.func(_obj) | state
        raise ValueError(f'Excepted {self.type_name}, but got {get_type_name(get_base_type(_obj))}')

    def __repr__(self):
        return f"SerializationMethod({{{self.type_name}: {self.func}}})"


def serialization_method(_type):
    def decorator(func):
        return SerializationMethod(_type, staticmethod(func))

    return decorator


class AbstractSerialization:
    _methods: dict
    _dataclass_name = 'dataclass'

    def __init__(self):
        self._methods = {}
        for k in self.__dir__():
            v = self.__getattribute__(k)
            if isinstance(v, SerializationMethod):
                self._methods[v.type_name] = v

    def __repr__(self):
        return self._methods.__repr__()

    def serialize(self, *args: Any):
        state = {}
        for arg in args:
            _type = get_base_type(arg.__class__)
            type_name = get_type_name(_type)
            try:
                state = self._methods[type_name].serialize(arg, state=state)
            except KeyError:
                error = ValueError(f'{type_name} is unrecognizable')
                try:
                    state = getattr(self, 'dataclass').serialize(arg, state=state)
                except KeyError:
                    raise error
            return state


class BaseSerialization(AbstractSerialization):
    @serialization_method(BaseModel)
    def pydantic(self):
        return self.dict()

    @serialization_method(object)
    def dataclass(self):
        raise NotImplemented()
