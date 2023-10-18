Feature: Sending HTTP request with authentication

    As a developer,
    I want to send requests with authentication,
    in order to test a REST API requiring authentication.

    Scenario: Authentication with bearer token
        Given all services are started
        When MY REQUEST WITH AUTH is requested
        Then service responds OK
