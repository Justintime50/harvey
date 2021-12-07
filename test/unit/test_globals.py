from harvey.globals import Global


def test_repo_name(mock_webhook):
    result = Global.repo_name(mock_webhook)

    assert result == 'test-repo-name'


def test_full_name(mock_webhook):
    result = Global.repo_full_name(mock_webhook)

    assert result == 'test_user/test-repo-name'


def test_author_name(mock_webhook):
    result = Global.repo_commit_author(mock_webhook)

    assert result == 'test_user'


def test_repo_url(mock_webhook):
    result = Global.repo_url(mock_webhook)

    assert result == 'https://test-url.com'


def test_repo_owner_name(mock_webhook):
    result = Global.repo_owner_name(mock_webhook)

    assert result == 'test_owner'


def test_repo_commit_id(mock_webhook):
    result = Global.repo_commit_id(mock_webhook)

    assert result == '123456'
