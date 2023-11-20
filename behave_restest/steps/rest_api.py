from copy import deepcopy
from http import HTTPStatus
from importlib import import_module
import json
from multiprocessing.pool import ThreadPool
import os
from pathlib import Path
from socket import gethostname

from behave import given, then, when
from pytest_httpserver import BlockingHTTPServer
import requests

from helpers import Response, UrlTemplate, ValueCapture

BEHAVE_RESTEST_SELF_TEST = os.environ.get('BEHAVE_RESTEST_SELF_TEST', 'no') in ['on', 'yes', '1']

# If the service is running in a container, an accessible host can be configured:
MOCK_SERVER_HOST = os.environ.get('MOCK_SERVER_HOST', gethostname())


@given(u'all services are started')
def step_impl(context):
    context.mock_server = create_http_server(context, host=MOCK_SERVER_HOST)

    if BEHAVE_RESTEST_SELF_TEST:
        context.fake_service = create_http_server(context)
        context.base_url = context.fake_service.url_for('')
    else:
        raise NotImplementedError


def create_http_server(context, host='localhost'):
    server = BlockingHTTPServer(host=host, timeout=9)
    server.start()
    context.add_cleanup(stop_http_server, server)
    return server


def stop_http_server(server):
    if server.is_running():
        server.stop()

    # Check if the service has made any request where no assertion was called on it from the test:
    server.check_assertions()

    server.clear()


@when(u'{request_descriptor} is requested')
def step_impl(context, request_descriptor):
    request = get_request(context, request_descriptor)

    replace_url_templates(context.mock_server, request.json)

    context.last_response = do_async(context, request.send, context.base_url)

    if BEHAVE_RESTEST_SELF_TEST:
        context.fake_response_handler = context.fake_service.assert_request(
            request.endpoint,
            method=request.method,
            headers=request.headers,
            **get_arg_for_request_body(request),
        )


def get_request(context, request_descriptor):
    return get_test_data('REQUEST', context, request_descriptor)


def get_test_data(suffix, context, descriptor):
    return deepcopy(
        getattr(import_module(Path(context.feature.filename).stem), '_'.join(descriptor.split() + [suffix]))
    )


def replace_url_templates(server, data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, UrlTemplate):
                data[key] = server.url_for(value)
            else:
                replace_url_templates(server, value)


def do_async(context, method, *args):
    def clean(pool):
        pool.close()
        pool.terminate()

    pool = ThreadPool(1)
    context.add_cleanup(clean, pool)

    return pool.apply_async(method, args)


def get_arg_for_request_body(request):
    return dict(data=request.data) if request.json is None else dict(json=request.json)


@then(u'service responds {status_code}')
@then(u'service responds {status_code} with {response_descriptor}')
def step_impl(context, status_code, response_descriptor=None):
    response = get_response(context, response_descriptor)

    if BEHAVE_RESTEST_SELF_TEST:
        def replace_value_capture_with_random_value(data):
            def random_value_for_value_capture(obj):
                assert isinstance(obj, ValueCapture)
                return '-'.join(filter(None, [obj._name, str(id(obj))]))

            return json.loads(json.dumps(data, default=random_value_for_value_capture))

        respond, fake_response = (
            context.fake_response_handler.respond_with_data,
            response.body,
        ) if type(response) is str else (
            context.fake_response_handler.respond_with_json,
            replace_value_capture_with_random_value(response.body),
        )

        response_headers = {
            key: 'TSESSIONID=abc123 ; Path=/test/; HttpOnly' if key == 'Set-Cookie' else value
            for key, value in response.headers.items()
        }

        respond(fake_response, status=getattr(HTTPStatus, status_code), headers=response_headers)

    actual_response = context.last_response.get(timeout=9)

    assert_responses_match(actual_response, response, status_code)


def assert_responses_match(actual: requests.Response, expected: Response, status_code):
    assert all(header in actual.headers.items() for header in expected.headers.items())

    try:
        actual_body = actual.json()
    except requests.exceptions.JSONDecodeError:
        actual_body = actual.text

    assert (actual.status_code, actual_body) == (getattr(HTTPStatus, status_code), expected.body), \
        f'actual response: {actual.status_code, actual_body}'


def get_response(context, response_descriptor):
    response = get_test_data('RESPONSE', context, response_descriptor) if response_descriptor else ''

    return response if isinstance(response, Response) else Response(body=response)


@then(u'service requests {request_descriptor}')
def step_service_requests(context, request_descriptor):
    request = get_request(context, request_descriptor)

    if BEHAVE_RESTEST_SELF_TEST:
        context.last_mock_response = do_async(context, request.send, context.mock_server.url_for(''))

    context.mock_response_handler = context.mock_server.assert_request(
        request.endpoint,
        method=request.method,
        headers=request.headers,
        **get_arg_for_request_body(request),
        timeout=9,
    )


@when(u'{status_code} is responded')
@when(u'{status_code} with {response_descriptor} is responded')
def step_impl(context, status_code, response_descriptor=None):
    response = get_response(context, response_descriptor)

    (
        context.mock_response_handler.respond_with_data
        if type(response.body) is str else
        context.mock_response_handler.respond_with_json
    )(
        response.body, status=getattr(HTTPStatus, status_code), headers=response.headers
    )

    if BEHAVE_RESTEST_SELF_TEST:
        assert_responses_match(context.last_mock_response.get(timeout=9), response, status_code)


@then(u'service exchanges {request_descriptor}')
def step_impl(context, request_descriptor):
    step_service_requests(context, request_descriptor)

    context.mock_response_handler.respond_with_data('', HTTPStatus.OK)

    if BEHAVE_RESTEST_SELF_TEST:
        assert_responses_match(context.last_mock_response.get(timeout=9), Response(), 'OK')
