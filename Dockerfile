FROM python:3.7

COPY harvey /var/www/html/harvey
COPY app.py /var/www/html/app.py
COPY requirements.txt /var/www/html/requirements.txt

RUN pip install -r /var/www/html/requirements.txt

CMD ["python", "./var/www/html/app.py"]
