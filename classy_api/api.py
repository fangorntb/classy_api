from functools import wraps

import requests
from requests import Response


def methods_factory(method):
    def decorator_factory_call(route: str, post_logic: callable = lambda self, response: None) -> callable:
        def decorator(func):
            @wraps(func)
            def wrapped(self, *args, **kwargs) -> Response:
                self.data = None
                self.params = None
                self.json = None
                self.files = None
                self.method = method
                self.route = route
                func(self, *args, **kwargs)
                response = self._send()
                post_logic(self, response, )
                return response

            return wrapped

        return decorator

    return decorator_factory_call


get = methods_factory('get')
post = methods_factory('post')
delete = methods_factory('delete')
put = methods_factory('put')
patch = methods_factory('patch')


class BaseAPI:
    def __init__(self, url: str):
        self.url = url
        self.json = None
        self.params = None
        self.data = None
        self.headers = None
        self.method = None
        self.route = None
        self.files = None

    def _send(self, ):
        return requests.request(
            self.method,
            self.url + self.route,
            params=self.params,
            json=self.json,
            headers=self.headers,
            data=self.data,
            files=self.files,
            verify=False
        )
