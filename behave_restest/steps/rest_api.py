from copy import deepcopy
from http import HTTPStatus
from importlib import import_module
from multiprocessing.pool import ThreadPool
import os
from pathlib import Path

from behave import given, then, when
from pytest_httpserver import HTTPServer

BEHAVE_RESTEST_SELF_TEST = os.environ.get('BEHAVE_RESTEST_SELF_TEST', 'no') in ['on', 'yes', '1']


@given(u'all services are started')
def step_impl(context):
    if BEHAVE_RESTEST_SELF_TEST:
        context.fake_service = create_http_server(context)
        context.base_url = context.fake_service.url_for('')
    else:
        raise NotImplementedError


def create_http_server(context):
    server = HTTPServer(host='localhost')
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

    if BEHAVE_RESTEST_SELF_TEST:
        context.fake_response_handler = context.fake_service.expect_request(
            request.endpoint,
            method=request.method,
            **get_arg_for_request_body(request),
        )

    context.last_response = pool.apply_async(request.send, (context.base_url,))


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
def step_impl(context, status_code):
    if BEHAVE_RESTEST_SELF_TEST:
        context.fake_response_handler.respond_with_data('', status=getattr(HTTPStatus, status_code))

    actual_response = context.last_response.get(timeout=9)

    assert actual_response.status_code == getattr(HTTPStatus, status_code), \
        f'actual response: {actual_response.status_code, actual_response.text}'
