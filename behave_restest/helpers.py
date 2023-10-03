import logging
from typing import Callable

import requests

JsonSerializable = dict[str, 'JsonSerializable'] | list['JsonSerializable'] | int | float | bool | None


class Request(requests.Request):
    def __init__(self, *args, endpoint, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = endpoint

    @property
    def json(self) -> JsonSerializable:
        return self._json() if callable(self._json) else self._json

    @json.setter
    def json(self, value: JsonSerializable | Callable[[], JsonSerializable]):
        self._json = value

    def send(self, base_url):
        self.url = base_url + self.endpoint

        prepared_request = self.prepare()

        with requests.Session() as session:
            return session.send(prepared_request)


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
