import time

import pytest

from preston_new import Preston


@pytest.fixture
def empty():
    return Preston()


@pytest.fixture
def sample():
    return Preston(
        version='1',
        client_id='2',
        client_secret='3',
        callback_url='4',
        scope='5',
        access_token='6',
        access_expiration='7',
        refresh_token='8',
        no_update_token=True
    )


def test_starting_point(empty):
    assert empty.cache is not None
    assert empty.spec is None
    assert empty.version is not None


def test_kwargs_setters(sample):
    assert sample.cache is not None
    assert sample.spec is None
    assert sample.version == '1'
    assert sample.client_id == '2'
    assert sample.client_secret == '3'
    assert sample.callback_url == '4'
    assert sample.scope == '5'
    assert sample.access_token == '6'
    assert sample.access_expiration == '7'
    assert sample.refresh_token == '8'


def test_copy(sample):
    new = sample.copy()
    new.access_token = None
    assert sample.access_token is not None


def test_get_authorization_headers(empty):
    expected = 'Basic c29tZV9jbGllbnRfaWQ6c29tZV9jbGllbnRfc2VjcmV0'
    empty.client_id = 'some_client_id'
    empty.client_secret = 'some_client_secret'
    assert expected == empty._get_authorization_headers()['Authorization']


def test_get_path_for_op_id(empty):
    empty.spec = {
        'paths': {
            'a': {
                'get': {
                    'operationId': 'a-id'
                }
            },
            'b': {
                'put': {
                    'operationId': 'b-id'
                }
            },
            'c': {
                'delete': {
                    'operationId': 'c-id'
                }
            }
        }
    }
    assert empty._get_path_for_op_id('a-id') == 'a'
    assert empty._get_path_for_op_id('b-id') == 'b'
    assert empty._get_path_for_op_id('c-id') == 'c'
    assert empty._get_path_for_op_id('d-id') is None


def test_is_access_token_expired(empty):
    empty.access_expiration = 0
    assert empty._is_access_token_expired()
    empty.access_expiration = time.time() + 1000
    assert not empty._is_access_token_expired()


def test_get_authorize_url(sample):
    expected = 'https://login.eveonline.com/oauth/authorize?response_type=code&redirect_uri=4&client_id=2&scope=5'
    assert sample.get_authorize_url() == expected


def test_update_access_token_header(sample):
    assert 'Authorization' not in sample.session.headers
    sample._update_access_token_header()
    assert sample.session.headers['Authorization'] == 'Bearer 6'


def test_insert_vars(empty):
    data = dict(foo='bar', bar='baz')
    path = '/foo/bar'
    p = empty._insert_vars(path, data)
    assert p == path
    path = '/foo/{bar}'
    p = empty._insert_vars(path, data)
    assert p == '/foo/baz'
    path = '/{foo}/bar'
    p = empty._insert_vars(path, data)
    assert p == '/bar/bar'
    path = '/{foo}/{bar}'
    p = empty._insert_vars(path, data)
    assert p == '/bar/baz'


def test_whoami_unauth(empty):
    assert empty.whoami() == {}
