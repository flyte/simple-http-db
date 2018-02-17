Simple HTTP DB
==============

This is a simple HTTP (Flask) server which accepts HTTP POSTs to any endpoint,
then saves the body data back to a Redis server. The data can be retrieved
again by doing an HTTP GET to the same endpoint.

Installation and Usage
----------------------

#### Docker

Use Docker Compose to bring up a Redis server as well as the HTTP server:

```bash
docker-compose up
```

Build and bring up the HTTP server on its own:

```bash
docker build . --tag simple-http-db
docker run -ti --rm -p 5000:5000 -e REDIS_HOST=my.redis.host simple-http-db
```

Or use the pre-built version from Docker Hub:

```bash
docker run -ti --rm -p 5000:5000 -e REDIS_HOST=my.redis.host flyte/simple-http-db
```

#### Python

This project uses pipenv to install and manage virtualenvs. To install
requirements and run this project:

```bash
pipenv install
pipenv run python server.py
```

The server will listen on port 5000 by default.
