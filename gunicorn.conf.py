import os

from dotenv import load_dotenv

# Additional details on configuring Gunicorn can be found here:
# https://github.com/benoitc/gunicorn/blob/master/examples/example_config.py

load_dotenv()
harvey_host = os.getenv('HOST', '127.0.0.1')
harvey_port = os.getenv('PORT', '5000')
loglevel = os.getenv('LOG_LEVEL', 'info').lower()

bind = f'{harvey_host}:{harvey_port}'
worker_class = 'gthread'
