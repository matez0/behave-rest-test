import logging
from typing import Callable

import requests

JsonSerializable = dict[str, 'JsonSerializable'] | list['JsonSerializable'] | int | float | bool | str | None


class Request(requests.Request):
    def __init__(self, *args, endpoint, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = endpoint

    @property
    def endpoint(self) -> str:
        return self._endpoint() if callable(self._endpoint) else self._endpoint

    @endpoint.setter
    def endpoint(self, value: str | Callable[[], str]):
        self._endpoint = value

    @property
    def headers(self) -> dict[str, str]:
        return self._headers() if callable(self._headers) else self._headers

    @headers.setter
    def headers(self, value: dict[str, str] | Callable[[], dict[str, str]]):
        self._headers = value

    @property
    def json(self) -> JsonSerializable:
        return self._json() if callable(self._json) else self._json

    @json.setter
    def json(self, value: JsonSerializable | Callable[[], JsonSerializable]):
        self._json = value

    def send(self, base_url):
        self.url = base_url + self.endpoint

        # If `self.auth` object would need something from `self`, it can be provided here.
        prepared_request = self.prepare()

        with requests.Session() as session:
            return session.send(prepared_request)


class Response:
    def __init__(
        self,
        headers: dict[str, str] | Callable[[], dict[str, str]] | None = None,
        body: str | JsonSerializable | Callable[[], str | JsonSerializable] = '',
    ):
        self._headers = headers or {}
        self._body = body

    @property
    def headers(self) -> dict[str, str]:
        return self._headers() if callable(self._headers) else self._headers

    @headers.setter
    def headers(self, value: dict[str, str] | Callable[[], dict[str, str]]):
        self._headers = value

    @property
    def body(self) -> str | JsonSerializable:
        return self._body() if callable(self._body) else self._body

    @body.setter
    def body(self, value: str | JsonSerializable | Callable[[], str | JsonSerializable]):
        self._body = value


class ValueCapture:
    value: JsonSerializable = None
    _name: str

    @classmethod
    def create(cls, name: str = '') -> 'ValueCapture':
        """
        Creates an object to capture a value when the object is matched with that value.

        The captured value is accessible through the `value` attribute, which is updated at each matching.

        The `value` attribute refers to the same object even after deepcopy, as it is a class attribute.

        The `name` is used for debugging purposes.
        """
        class _ValueCapture(ValueCapture):
            _name = name

        return _ValueCapture()

    def __new__(cls):
        if cls is ValueCapture:
            raise TypeError(f'{cls.__name__} is not to be instantiated, use create method')

        return super().__new__(cls)

    def __eq__(self, other) -> bool:
        self.__class__.value = other
        logging.info(f'\n--------\n{self._name or f"value_capture_{id(self)}"}={other}\n--------\n')
        return True
