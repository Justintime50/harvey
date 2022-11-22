import os

from dotenv import load_dotenv


load_dotenv()  # Must remain at the top of this file


class Config:
    # User configurable settings
    allowed_branches = [branch.strip().lower() for branch in os.getenv('ALLOWED_BRANCHES', 'main,master').split(',')]
    deploy_timeout = int(os.getenv('DEPLOY_TIMEOUT', 1800))  # Default is 30 minutes
    git_timeout = int(os.getenv('GIT_TIMEOUT', 300))  # Default is 5 minutes
    pagination_limit = int(os.getenv('PAGINATION_LIMIT', 20))
    deploy_on_tag = os.getenv('DEPLOY_ON_TAG', True)  # Whether a tag pushed will trigger a deploy or not
    use_slack = os.getenv('USE_SLACK')
    webhook_secret = os.getenv('WEBHOOK_SECRET', '')
    slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
    slack_channel = os.getenv('SLACK_CHANNEL', 'general')
    harvey_path = os.getenv('HARVEY_PATH', os.path.expanduser('~/harvey'))

    # Harvey settings
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    harvey_version = '0.21.0'
    supported_deployments = {
        'deploy',
        'pull',
    }
    default_deployment = 'deploy'
    projects_path = os.path.join(harvey_path, 'projects')
    database_path = os.path.join(harvey_path, 'databases')
    database_file = os.path.join(database_path, 'database.sqlite')
    logger_name = 'harvey'
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_location = os.path.join(harvey_path, 'logs', 'harvey')
    sentry_url = os.getenv('SENTRY_URL')
