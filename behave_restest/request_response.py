from helpers import Request

MY_REQUEST_REQUEST = Request(
    endpoint='/host/path/',
    method='POST',
    json={
        "fieldOne": "value-one",
        "fieldTwo": "value-two",
    },
)
