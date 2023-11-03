from helpers import Request

MY_REQUEST_REQUEST = Request(
    endpoint='/my/path/',
    method='POST',
    json={
        "fieldOne": "value-one",
        "fieldTwo": "value-two",
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
    endpoint='/callback/with/result/',  # The mock server base URL has to be configured as a base URL for the server.
    method='POST',
    json={
        "result": "success",
    },
)
