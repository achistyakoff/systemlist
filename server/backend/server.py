from flask import Flask, jsonify, request
import psycopg2
import os

app = Flask(__name__)

# Function to create a connection to the PostgreSQL database
def create_connection():
    connection = psycopg2.connect(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )
    return connection

# Function to check the existence of the 'servers' table and create it if it doesn't exist
def create_table_if_not_exists():
    connection = create_connection()
    cursor = connection.cursor()
    # Query to check the existence of the 'servers' table
    check_table_query = "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name = 'servers')"
    cursor.execute(check_table_query)
    table_exists = cursor.fetchone()[0]
    if not table_exists:
        # Query to create the 'servers' table
        create_table_query = """
            CREATE TABLE servers (
                hostname VARCHAR(255) PRIMARY KEY,
                environment VARCHAR(255),
                solution VARCHAR(255),
                system VARCHAR(255),
                os VARCHAR(255),
                tags VARCHAR(255) []
            )
        """
        cursor.execute(create_table_query)
        connection.commit()
    cursor.close()
    connection.close()

# Call the function to check the existence of the 'servers' table and create it if it doesn't exist
create_table_if_not_exists()

# Route to get all servers
@app.route('/api/servers', methods=['GET'])
def get_servers():
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM servers"
    cursor.execute(query)
    servers = cursor.fetchall()
    cursor.close()
    connection.close()
    server_list = []
    for server in servers:
        server_dict = {
            'hostname': server[0],
            'environment': server[1],
            'solution': server[2],
            'system': server[3],
            'os': server[4],
            'tags': server[5]
        }
        server_list.append(server_dict)
    return jsonify(server_list)

# Route to get server by hostname
@app.route('/api/servers/<hostname>', methods=['GET'])
def get_server_by_hostname(hostname):
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM servers WHERE hostname = %s"
    cursor.execute(query, (hostname,))
    server = cursor.fetchone()
    cursor.close()
    connection.close()
    if server:
        server_dict = {
            'hostname': server[0],
            'environment': server[1],
            'solution': server[2],
            'system': server[3],
            'os': server[4],
            'tags': server[5]
        }
        return jsonify(server_dict)
    else:
        return jsonify({'error': 'Server not found'}), 404

# Route for creating records in the table with hostname validation
@app.route('/servers', methods=['POST'])
def create_server():
    data = request.json
    hostname = data.get('hostname')
    connection = create_connection()
    cursor = connection.cursor()

    # Check if a record with the given hostname already exists
    cursor.execute('SELECT * FROM servers WHERE hostname = %s', (hostname,))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify({'message': 'Server with the given hostname already exists'}), 409

    # Create a new record in the table
    cursor.execute(
        '''
        INSERT INTO servers (hostname, environment, solution, system, os, tags)
        VALUES (%s, %s, %s, %s, %s, %s)
        ''',
        (hostname, data.get('environment'), data.get('solution'), data.get('system'), data.get('os'), data.get('tags'))
    )

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Server created successfully'}), 201

# Route to update server by hostname
@app.route('/api/servers/<hostname>', methods=['PUT'])
def update_server_by_hostname(hostname):
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM servers WHERE hostname = %s"
    cursor.execute(query, (hostname,))
    server = cursor.fetchone()
    if server:
        new_data = request.get_json()
        update_query = "UPDATE servers SET environment = %s, solution = %s, system = %s, os = %s, tags = %s WHERE hostname = %s"
        cursor.execute(update_query, (
            new_data['environment'],
            new_data['solution'],
            new_data['system'],
            new_data['os'],
            new_data['tags'],
            hostname
        ))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Server updated successfully'})
    else:
        cursor.close()
        connection.close()
        return jsonify({'error': 'Server not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
