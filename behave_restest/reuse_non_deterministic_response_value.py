from helpers import JsonSerializable, Request, ValueCapture

CREATE_MY_ITEM_REQUEST = Request(
    endpoint='/item/create/',
    method='POST',
    json={
        "name": "my-item-name",
        "color": "my-item-color",
    },
)

MY_ITEM_ID_RESPONSE = {
    "itemId": ValueCapture.create('item_id'),
}


class ActionRequestPath:
    def __call__(self) -> str:
        return f'/item/action/{MY_ITEM_ID_RESPONSE["itemId"].value}/'


ACTION_WITH_MY_ITEM_ID_IN_PATH_REQUEST = Request(
    endpoint=ActionRequestPath(),
    method='GET',
    data='',
)


class ActionRequestPayload:
    def __init__(self):
        self.value = {
            "actionRequestField": "action-request-value"
        }

    def __call__(self) -> JsonSerializable:
        self.value["itemId"] = MY_ITEM_ID_RESPONSE["itemId"].value
        return self.value


ACTION_WITH_MY_ITEM_ID_IN_PAYLOAD_REQUEST = Request(
    endpoint='/item/action/',
    method='PATCH',
    json=ActionRequestPayload(),
)
