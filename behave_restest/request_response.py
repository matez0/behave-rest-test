from helpers import Request, Response

MY_REQUEST_REQUEST = Request(
    endpoint='/my/path/',
    method='POST',
    json={
        "fieldOne": "value-one",
        "fieldTwo": "value-two",
    },
)

MY_JSON_RESPONSE_RESPONSE = Response(
    body={
        "responseField": "response-value",
    },
)

MY_TEXT_RESPONSE_RESPONSE = "response-text"
