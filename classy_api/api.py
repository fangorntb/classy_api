from enum import Enum
from functools import partial
from types import NoneType
from typing import Any

from requests import request

from .serialization import BaseSerialization, AbstractSerialization


class MethodEnum(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'


BASE_PARAMS = 'json,params,files,data,headers'.split(',')


def get_prompt(p: str, params: dict):
    for k, v in params.items():
        p = p.replace(f'{{{k}}}', f'{v}')
    return p


def mount_url(base_url: str, sub_url: str, params: dict) -> str:
    url = base_url + sub_url
    return get_prompt(url, params)


def is_params_type(param):
    return type(param) in (int, float, NoneType, bool, str)


class APIMethod:
    def __init__(
            self,
            method_type,
            func: callable,
            serialization: AbstractSerialization,
            base_api: 'BaseAPI',
            sub_url: str,
    ):
        self.scope = dict.fromkeys(BASE_PARAMS)
        self.serialization = serialization
        self.base_api = base_api
        self.func = func
        self.method_type = method_type
        self.sub_url = sub_url
        self.latest_result = None

    def __call__(
            self,
            *args,
            **kwargs,
    ):
        dct = self.scope
        from_method = self.func(self.base_api, *args, **kwargs) or {}
        for k, v in from_method.items():
            dct[k] = v
        for param in BASE_PARAMS:
            if dct.get(param) is None:
                dct[param] = {}

        json = dct['json']
        files = dct['files']
        data = dct['data']
        params = dct['params']
        url = mount_url(self.base_api.baseurl, self.sub_url, params)
        self.latest_result = request(
            self.method_type,
            url,
            json=json,
            params=params,
            files=files,
            data=data,
            headers=self.base_api.headers | dct['headers'],
        )
        return self.latest_result


def _method_decorator_factory(
        sub_url: str,
        method: str,
        serialization: AbstractSerialization,
):
    def _decorator(func):
        m_name = func.__name__

        def _wrapped(self, *args, **kwargs):
            api_method = getattr(self, m_name)
            if not isinstance(api_method, APIMethod):
                api_method = APIMethod(method, func, serialization, self, sub_url)
                setattr(self, m_name, api_method)
            return api_method.__call__(*args, **kwargs)

        return _wrapped

    return _decorator


class BaseAPI:
    def __init__(
            self,
            base_url: str,
            base_headers: dict = None,
    ):
        self.baseurl = base_url
        self.headers = {} if base_headers is None else base_headers


get = partial(_method_decorator_factory, serialization=BaseSerialization(), method=MethodEnum.GET.value)
post = partial(_method_decorator_factory, serialization=BaseSerialization(), method=MethodEnum.POST.value)
patch = partial(_method_decorator_factory, serialization=BaseSerialization(), method=MethodEnum.PATCH.value)
delete = partial(_method_decorator_factory, serialization=BaseSerialization(), method=MethodEnum.DELETE.value)
put = partial(_method_decorator_factory, serialization=BaseSerialization(), method=MethodEnum.PUT.value)
