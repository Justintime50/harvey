from unittest.mock import (
    Mock,
    patch,
)

from harvey.containers import Container


@patch('logging.Logger.debug')
@patch('docker.from_env')
def test_create_client(mock_client, mock_logger):
    _ = Container.create_client()

    mock_client.assert_called_once()


@patch('logging.Logger.debug')
@patch('docker.from_env')
def test_get_container(mock_client, mock_logger, mock_tag):
    mock_docker_client = mock_client
    _ = Container.get_container(mock_docker_client, mock_tag)

    mock_logger.assert_called()
    mock_client.containers.get.assert_called_once_with(mock_tag)


@patch('logging.Logger.debug')
@patch('docker.from_env')
def test_list_containers(mock_client, mock_logger, mock_tag):
    mock_docker_client = mock_client
    _ = Container.list_containers(mock_docker_client)

    mock_logger.assert_called()
    mock_client.containers.list.assert_called_once()


@patch('logging.Logger.info')
@patch('time.sleep', return_value=None)
@patch('harvey.containers.Container.get_container', return_value=Mock(status='running'))
@patch('docker.from_env')
def test_run_container_healthcheck_success(
    mock_client, mock_container, mock_sleep, mock_logger, mock_container_name, mock_webhook
):
    mock_docker_client = mock_client
    healthcheck = Container.run_container_healthcheck(mock_docker_client, mock_container_name, mock_webhook)

    mock_logger.assert_called()
    mock_container.assert_called_once_with(mock_docker_client, mock_container_name)
    assert healthcheck is True


@patch('logging.Logger.info')
@patch('time.sleep', return_value=None)
@patch('harvey.containers.Container.get_container', return_value=Mock(status='exited'))
@patch('docker.from_env')
def test_run_container_healthcheck_failed(
    mock_client, mock_container, mock_sleep, mock_logger, mock_container_name, mock_webhook
):
    """This test checks that if a healthcheck fails, we properly retry.

    This test asserts we never succeed and abandon the retries after the max attempts are made."""
    mock_docker_client = mock_client
    healthcheck = Container.run_container_healthcheck(mock_docker_client, mock_container_name, mock_webhook)

    mock_logger.assert_called()
    mock_container.assert_called_with(mock_docker_client, mock_container_name)
    assert mock_container.call_count == 5
    assert healthcheck is False
