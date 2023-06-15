# Backend Server

This is a backend server application for handling server data. It is built using Python and Flask, and connects to a PostgreSQL database.

## Prerequisites

- Docker
- PostgreSQL database

## Configuration

Before running the server, make sure to configure the following environment variables:

    DB_HOST: The hostname or IP address of the PostgreSQL database server.
    DB_PORT: The port number on which the PostgreSQL database server is running.
    DB_NAME: The name of the PostgreSQL database.
    DB_USER: The username to connect to the PostgreSQL database.
    DB_PASSWORD: The password to connect to the PostgreSQL database.

### Start

To start the backend server, run the following command:
    `docker run -e DB_HOST="hostname_of_the_database_server" -e DB_PORT="port_of_the_database_server" -e DB_USER="username" -e DB_NAME="databade_name" -e DB_PASSWORD="db_password" -p 8000:8000 chistyakoff/systemlist:1.0`

### Usage

The server will start running on port 8000 by default. You can access the API endpoints using the following base URL:
    `http://localhost:8000`

## API Endpoints

    GET /servers: Get a list of all servers.
    GET /servers/{id}: Get details of a specific server.
    POST /servers: Create a new server.
    PUT /servers/{id}: Update the details of a server.
    DELETE /servers/{id}: Delete a server.

Refer to the API documentation for more details on request/response formats and parameters.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.