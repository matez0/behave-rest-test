Feature: Test HTTP request sent by the service under test

    As a developer,
    I want to check and respond to HTTP requests sent by my service,
    in order to test and control the interaction of my service with other servers.

    Background:
        Given all services are started
        When MY REQUEST is requested

    Scenario: Check request and respond with data
        Then service requests ADDITIONAL INFO FROM ANOTHER SERVER
        When OK with ADDITIONAL INFO is responded
        Then service responds OK

    Scenario: Check request and respond without data
        Then service requests CREATE ITEM FROM ANOTHER SERVER
        When CREATED is responded
        Then service responds OK

    Scenario: Check request and respond automatically with OK
        Then service exchanges RESULTS WITH ANOTHER SERVER
        And service responds OK
