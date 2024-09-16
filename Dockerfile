FROM python:3.12

# Helps with Docker logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies and Docker CLI from the 'docker.io' package
RUN apt-get update && \
    apt-get install -y curl gnupg lsb-release docker.io && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Docker Compose manually
RUN curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

COPY . .

RUN pip install -e .

EXPOSE 5000

ENTRYPOINT [ "uwsgi", "--ini", "uwsgi.ini" ]
