Feature: Test sending HTTP request and checking response

    As a developer,
    I want to send HTTP request and check the response,
    in order to test the REST API of my service.

    Scenario: Response without body
        Given all services are started
        When MY REQUEST is requested
        Then service responds OK
