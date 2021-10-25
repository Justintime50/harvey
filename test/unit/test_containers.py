from unittest.mock import Mock, patch

import pytest

from harvey.containers import Container
from harvey.globals import Global


@pytest.mark.skip('Skipping for now as I am unable to mock the proper function')
@patch('docker.client.DockerClient.from_env')
def test_create_client(mock_client):
    _ = Container.create_client()

    mock_client.assert_called_once()


@patch('harvey.containers.Container.create_client')
@patch('docker.models.containers.ContainerCollection.get')
def test_get_container(mock_request, mock_client, mock_tag):
    _ = Container.get_container(mock_tag)

    mock_client.assert_called_once()
    # mock_request.assert_called_once_with(mock_tag)  # TODO: Add this test, e2e tested fine


@patch('harvey.containers.Container.create_client')
@patch('docker.models.containers.ContainerCollection.list')
def test_list_containers(mock_request, mock_client, mock_tag):
    _ = Container.list_containers()

    mock_client.assert_called_once()
    # mock_request.assert_called_once_with(mock_tag)  # TODO: Add this test, e2e tested fine


@patch('time.sleep', return_value=None)
@patch('harvey.containers.Container.get_container', return_value=Mock(status='running'))
def test_run_container_healthcheck_success(mock_container, mock_sleep, mock_webhook):
    healthcheck = Container.run_container_healthcheck(mock_webhook)

    mock_container.assert_called_once_with(Global.repo_name(mock_webhook))
    assert healthcheck is True


@patch('time.sleep', return_value=None)
@patch('harvey.containers.Container.get_container', return_value=Mock(status='exited'))
def test_run_container_healthcheck_failed(mock_container, mock_sleep, mock_webhook):
    """This test checks that if a healthcheck fails, we properly retry"""
    healthcheck = Container().run_container_healthcheck(mock_webhook)

    mock_container.assert_called_with(Global.repo_name(mock_webhook))
    assert mock_container.call_count == 5
    assert healthcheck is False
