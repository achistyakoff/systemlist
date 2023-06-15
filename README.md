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

    docker run -e DB_HOST="hostname_of_the_database_server" -e DB_PORT="port_of_the_database_server" -e DB_USER="username" -e DB_NAME="databade_name" -e DB_PASSWORD="db_password" -p 8000:8000 chistyakoff/systemlist:1.0

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

## Environment Variables

| Variable    | Description                  |
|-------------|------------------------------|
| hostname    | Hostname of the server       |
| environment | Server environment           |
| solution    | Solution the server belongs to |
| system      | System the server runs on    |
| os          | Operating system of the server |
| tags        | Tags associated with the server |

## Examples

To create a record using Postman, you can send a POST request to your backend server's API endpoint. Here's an example of how you can structure the request in Postman:

    Open Postman and create a new request.
    Set the HTTP method to POST.
    Enter the URL of your backend server's API endpoint where the record creation is handled (e.g., http://localhost:8000/servers).
    Add the necessary headers, such as Content-Type: application/json, to indicate that you're sending JSON data.
    In the request body, provide the JSON payload for the record you want to create. The payload should include the required data fields such as hostname, environment, solution, system, os, and tags.

Here's an example JSON payload:

    ```json
    {
        "hostname": "example-server",
        "environment": "production",
        "solution": "web",
        "system": "Linux",
        "os": "Ubuntu",
        "tags": ["tag1", "tag2"]
    }
    ```

    Send the request by clicking the "Send" button in Postman.

Ensure that your backend server's API endpoint is correctly configured to handle POST requests and process the JSON payload to create the record in the database.


## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.