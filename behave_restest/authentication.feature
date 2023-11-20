Feature: Sending HTTP request with authentication

    As a developer,
    I want to send requests with authentication,
    in order to test a REST API requiring authentication.

    Background:
        Given all services are started

    Scenario: Authentication with bearer token
        When MY REQUEST WITH AUTH is requested
        Then service responds OK

    Scenario: Authentication with cookie
        When MY LOGIN is requested
        Then service responds OK with COOKIE
        When MY REQUEST WITH COOKIE AUTH is requested
        Then service responds OK
