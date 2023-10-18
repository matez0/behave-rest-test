from hashlib import sha256
from time import time

import jwt
from requests import PreparedRequest
from requests.auth import AuthBase

from helpers import Request


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
