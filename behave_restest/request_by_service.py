from helpers import Request, UrlTemplate

CALLBACK_URL = UrlTemplate('/callback/with/result/')

MY_REQUEST_REQUEST = Request(
    endpoint='/my/path/',
    method='POST',
    json={
        "fieldOne": "value-one",
        "fieldTwo": "value-two",
        "callbackUrl": CALLBACK_URL,
    },
)

ADDITIONAL_INFO_FROM_ANOTHER_SERVER_REQUEST = Request(
    endpoint='/additional/info/',  # The mock server base URL has to be configured as a base URL for the server.
    method='GET',
    data='',
)

ADDITIONAL_INFO_RESPONSE = {
    "additionalInfo": "additional-info",
}

CREATE_ITEM_FROM_ANOTHER_SERVER_REQUEST = Request(
    endpoint='/item/create/',  # The mock server base URL has to be configured as a base URL for the server.
    method='POST',
    json={
        "name": "my-item-name",
        "color": "my-item-color",
    },
)

RESULTS_WITH_ANOTHER_SERVER_REQUEST = Request(
    endpoint=CALLBACK_URL,  # The service shall use the callback URL specified in the initial request.
    method='POST',
    json={
        "result": "success",
    },
)
