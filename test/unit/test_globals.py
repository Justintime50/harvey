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
    assert 'test-repo-name' == result


def test_full_name(_mock_webhook):
    result = Global.repo_full_name(_mock_webhook)
    assert 'test_user/test-repo-name' == result


def test_author_name(_mock_webhook):
    result = Global.repo_commit_author(_mock_webhook)
    assert 'test_user' == result


def test_repo_url(_mock_webhook):
    result = Global.repo_url(_mock_webhook)
    assert 'https://test-url.com' == result


def test_repo_owner_name(_mock_webhook):
    result = Global.repo_owner_name(_mock_webhook)
    assert 'test_owner' == result


def test_repo_commit_id(_mock_webhook):
    result = Global.repo_commit_id(_mock_webhook)
    assert 123456 == result
