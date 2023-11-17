from copy import deepcopy
from http import HTTPStatus
from importlib import import_module
import json
from multiprocessing.pool import ThreadPool
import os
from pathlib import Path

from behave import given, then, when
from pytest_httpserver import BlockingHTTPServer
import requests

from helpers import Response, ValueCapture

BEHAVE_RESTEST_SELF_TEST = os.environ.get('BEHAVE_RESTEST_SELF_TEST', 'no') in ['on', 'yes', '1']


@given(u'all services are started')
def step_impl(context):
    if BEHAVE_RESTEST_SELF_TEST:
        context.fake_service = create_http_server(context)
        context.base_url = context.fake_service.url_for('')
    else:
        raise NotImplementedError


def create_http_server(context):
    server = BlockingHTTPServer(host='localhost', timeout=9)
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

    pool = ThreadPool(1)
    context.add_cleanup(clean_request_pool, pool)

    context.last_response = pool.apply_async(request.send, (context.base_url,))

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


def clean_request_pool(pool):
    pool.close()
    pool.terminate()


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

        respond(fake_response, status=getattr(HTTPStatus, status_code), headers=response.headers)

    actual_response = context.last_response.get(timeout=9)

    assert all(header in actual_response.headers.items() for header in response.headers.items())

    try:
        actual_response_body = actual_response.json()
    except requests.exceptions.JSONDecodeError:
        actual_response_body = actual_response.text

    assert (actual_response.status_code, actual_response_body) == (getattr(HTTPStatus, status_code), response.body), \
        f'actual response: {actual_response.status_code, actual_response_body}'


def get_response(context, response_descriptor):
    response = get_test_data('RESPONSE', context, response_descriptor) if response_descriptor else ''

    return response if isinstance(response, Response) else Response(body=response)
