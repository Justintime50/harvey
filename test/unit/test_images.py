from test.unit.conftest import mock_response  # Remove once fixtures are fixed

import mock
import pytest
from harvey.globals import Global
from harvey.images import Image


@pytest.mark.parametrize('context', [('test'), (None)])
@mock.patch('subprocess.check_output')
def test_build_image(mock_subprocess, context, mock_webhook):
    # TODO: Mock the subprocess better to ensure it does what it's supposed to
    Image.build_image(
        {
            'pipeline': 'full',
            'language': 'python',
            'version': '3.9',
        },
        mock_webhook,
        context
    )
    mock_subprocess.assert_called_once()


@mock.patch('requests.get', return_value=mock_response(201))
def test_retrieve_image(mock_request):
    Image.retrieve_image(1)
    mock_request.assert_called_once_with(Global.BASE_URL + 'images/1/json')


@mock.patch('requests.get', return_value=mock_response(201))
def test_retrieve_all_images(mock_request):
    Image.retrieve_all_images()
    mock_request.assert_called_once_with(Global.BASE_URL + 'images/json')


@mock.patch('requests.delete', return_value=mock_response(201))
def test_remove_image(mock_request):
    Image.remove_image(1)
    mock_request.assert_called_once_with(
        Global.BASE_URL + 'images/1',
        json={'force': True},
        headers=Global.JSON_HEADERS
    )
