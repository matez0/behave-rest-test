Feature: Test reusing non-deterministic response value in a subsequent request

    One may get a token or an ID in a response of a REST API request
    that is needed as an input of another request.

    As a developer,
    I want to reuse a non-deterministic value from a response in a subsequent request,
    in order to test a sequence of requests depending on each other.

    Scenario: Reuse non-deterministic response value in a subsequent request payload
        Given all services are started

        When CREATE MY ITEM is requested
        Then service responds CREATED with MY ITEM ID

        When ACTION WITH MY ITEM ID IN PAYLOAD is requested
        Then service responds OK
