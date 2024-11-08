# A service for storing secret data

JSON API is a service that allows you to encrypt and store secret data with a limited lifetime. 

## The stack used

- [FastAPI](https://fastapi.tiangolo.com/) a modern, fast (high-performance) web framework for creating APIs.
- [PostgreSQL](https://www.postgresql.org) — a free object-relational database management system.
- [Uvicorn](https://www.uvicorn.org/) ASGI web server implementation for Python.
- [Pytest](https://docs.pytest.org/en/7.4.x/contents.html) a full-featured Python testing tool
- [Docker](https://docs.docker.com/get-started/overview/) an open platform for the development, delivery and launch of applications.
- [Docker compose](https://docs.docker.com/compose/) a tool for defining and running Docker multi-container applications. 


## Installation

### The procedure of actions:
1. Install Docker according to [instructions from the Docker website](https://docs.docker.com/engine/install/ubuntu/)

2. Clone the repository to the server:

    ```git clone https://github.com/DianaValishina/secret-generate-fastapi.git```

3. Go to the catalog with the service:

    ```cd secret-generate-fastapi```

4. If necessary, change the parameters in `docker-compose.yml`
5. Edit the file `.env`
   ```bash
   DB_HOST=db # production database host 
   DB_PORT=5432 # production database port 
   DB_NAME=postgres # production database name 
   DB_USER=postgres # production database user 
   DB_PASS=postgres # production database the user's password 
    ```

6. Start the service using Docker Compose:

    ```
    docker compose up -d
    ```
7. Check the functionality of the service according to the settings

## Stopping the service

To stop the service, run the following command:

   ```bash
   docker compose -p secret_marks  stop
   ```

## The work of the service
The service has two endpoints:

- `POST /generate` accepts a secret, a passphrase, returns the secret_key by which this secret can be obtained.
  Example of sending an HTTP request:
  ```bash
  curl -X 'POST' \
  'http://0.0.0.0:8000/generate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{ "secret_text": "string", "passphrase": "string", "auto_delete": "string"}'
  ```
  
- `GET /secrets/{secret_key}` accepts a passphrase as input and gives away the secret.
  Example of sending an HTTP request:
  ```bash
  curl -X 'GET' \
  'http://0.0.0.0:8000/secrets/<secret_key>' \
  -H 'accept: application/json'
  ```
Detailed documentation : `GET <fastapi_service>/docs` 

## Testing
Run the command
```
 pytest tests/
```
# secret-generate-fastapi
# secret-generate-fastapi
