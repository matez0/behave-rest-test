Feature: Test sending HTTP request and checking response

    As a developer,
    I want to send HTTP request and check the response,
    in order to test the REST API of my service.

    Background:
        Given all services are started

    Scenario: Response without body
        When MY REQUEST is requested
        Then service responds OK

    Scenario: Response with JSON body
        When MY REQUEST is requested
        Then service responds OK with MY JSON RESPONSE

    Scenario: Response with text body
        When MY REQUEST is requested
        Then service responds IM_A_TEAPOT with MY TEXT RESPONSE
