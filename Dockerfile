FROM python:3.12

# Helps with Docker logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Docker CLI
RUN apt-get update && \
    apt-get install -y curl gnupg lsb-release && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
    echo "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y docker-ce-cli

# Install Docker Compose manually
RUN curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Clean up to minimize image size
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install -e .

EXPOSE 5000

ENTRYPOINT [ "uwsgi", "--ini", "uwsgi.ini" ]
