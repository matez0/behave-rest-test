from hashlib import sha256
from time import time

import jwt
from requests import PreparedRequest
from requests.auth import AuthBase

from helpers import Request, Response, ValueCapture


class Auth(AuthBase):
    def __call__(self, request: PreparedRequest) -> PreparedRequest:
        request.headers["Authorization"] = f'Bearer {create_jwt_for_auth(request.url, request.body)}'
        return request


CLIENT_PRIVATE_KEY = '''
-----BEGIN PRIVATE KEY-----
MIGEAgEAMBAGByqGSM49AgEGBSuBBAAKBG0wawIBAQQgz7486xK/qUUgUMK6nwA/
OkBzNCJNrXuR6kZiqTrZkbGhRANCAAQMyUgu6L3KB835tGSvzQzxxUao8v5hPJyR
PNikuCNB0zFWw7inxIonBmJv6vNTbHnG772S4BaEUA8Q46o7krBV
-----END PRIVATE KEY-----
'''


def create_jwt_for_auth(request_url: str, request_body: bytes = b'') -> str:
    validity_period = 600
    token_payload = {
        "requestUrl": request_url,
        "requestBodyHash": sha256(request_body).hexdigest(),
        "exp": int(time()) + validity_period,
    }
    return jwt.encode(token_payload, CLIENT_PRIVATE_KEY, algorithm='ES256K')


MY_REQUEST_WITH_AUTH_REQUEST = Request(
    endpoint='/privileged/action/',
    method='POST',
    json={
        "fieldOne": "value-one",
        "fieldTwo": "value-two",
    },
    auth=Auth()
)

MY_LOGIN_REQUEST = Request(
    endpoint='/my/login/',
    method='POST',
    json={
        "username": "my-username",
        "password": "my-password",
    },
)

COOKIE_RESPONSE = Response(
    headers={
        "Set-Cookie": ValueCapture.create('cookie')
    }
)


class HeadersWithCookieAuth:
    def __call__(self) -> dict[str, str]:
        set_cookie = COOKIE_RESPONSE.headers['Set-Cookie']
        assert isinstance(set_cookie, ValueCapture)

        headers = {}

        if isinstance(set_cookie.value, str):
            headers["Cookie"] = set_cookie.value.split(';')[0].strip()

        return headers


MY_REQUEST_WITH_COOKIE_AUTH_REQUEST = Request(
    endpoint='/profile/settings/',
    method='POST',
    headers=HeadersWithCookieAuth(),
    json={
        "email": "nobody@nowhere.none",
        "notifications": "off",
    },
)
