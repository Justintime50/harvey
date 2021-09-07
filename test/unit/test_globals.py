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

    assert result == 123456


def test_github_webhook_ip_ranges():
    """Assert that localhost and the first and last IP address
    of each CIDR range is in the result. These may need to be updated
    when GitHub updates their list of ranges.

    You can use a tool such as https://www.subnet-calculator.com/cidr.php
    to assist in converting the annotations.
    """
    result = Global.github_webhook_ip_ranges()

    assert '127.0.0.1' in result
    assert '192.30.252.0' in result
    assert '192.30.255.255' in result
    assert '185.199.108.0' in result
    assert '185.199.111.255' in result
    assert '140.82.112.0' in result
    assert '140.82.127.255' in result
    assert '143.55.64.0' in result
    assert '143.55.79.255' in result
