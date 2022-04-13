FROM python:3.10
# TODO: Explore alpine image

# Install `Docker Compose` v2 and save it as `harvey-compose`
RUN curl -L "https://github.com/docker/compose/releases/download/v2.4.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/harvey-compose && \
    chmod +x /usr/local/bin/harvey-compose

COPY . .
RUN pip install -e .

WORKDIR /harvey

CMD ["python", "app.py"]
