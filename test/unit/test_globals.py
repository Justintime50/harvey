import pytest
from harvey.globals import Global


@pytest.fixture
def _mock_webhook():
    webhook = {
        "repository": {
            "name": "TEST-repo-name",
            "full_name": "TEST_user/TEST-repo-name",
            "ssh_url": "https://test-url.com",
            "owner": {
                "name": "TEST_owner"
            }
        },
        "commits": [
            {
                "id": 123456,
                "author": {
                    "name": "test_user"
                }
            }
        ]
    }
    return webhook


def test_repo_name(_mock_webhook):
    result = Global.repo_name(_mock_webhook)
    assert result == 'test-repo-name'


def test_full_name(_mock_webhook):
    result = Global.repo_full_name(_mock_webhook)
    assert result == 'test_user/test-repo-name'


def test_author_name(_mock_webhook):
    result = Global.repo_commit_author(_mock_webhook)
    assert result == 'test_user'


def test_repo_url(_mock_webhook):
    result = Global.repo_url(_mock_webhook)
    assert result == 'https://test-url.com'


def test_repo_owner_name(_mock_webhook):
    result = Global.repo_owner_name(_mock_webhook)
    assert result == 'test_owner'


def test_repo_commit_id(_mock_webhook):
    result = Global.repo_commit_id(_mock_webhook)
    assert result == 123456


def test_docker_project_name(_mock_webhook):
    result = Global.docker_project_name(_mock_webhook)
    assert result == 'test_owner-test-repo-name'
