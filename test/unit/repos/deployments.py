from unittest.mock import (
    mock_open,
    patch,
)

from harvey.repos.deployments import store_deployment_details


@patch('logging.Logger.debug')
def test_store_deployment_details(mock_logger, mock_output, mock_webhook):
    with patch('builtins.open', mock_open()):
        store_deployment_details(mock_webhook, mock_output)

        mock_logger.assert_called()
