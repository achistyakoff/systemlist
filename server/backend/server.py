from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import Json
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

def create_possible_fields_tables():
    # Connect to the database
    connection = create_connection()
    cursor = connection.cursor()
    
    # Create the possible_ tables if it don't exist
    try:
        # Check if the possible_fields table exists
        cursor.execute("CREATE TABLE IF NOT EXISTS possible_solution (solution VARCHAR(255) PRIMARY KEY)")
        cursor.execute("CREATE TABLE IF NOT EXISTS possible_environment (environment VARCHAR(255) PRIMARY KEY)")
        cursor.execute("CREATE TABLE IF NOT EXISTS possible_os (os VARCHAR(255) PRIMARY KEY)")
        cursor.execute("CREATE TABLE IF NOT EXISTS possible_tags (tags VARCHAR(255) PRIMARY KEY)")
        cursor.execute("CREATE TABLE IF NOT EXISTS possible_system (system VARCHAR(255) PRIMARY KEY)")
        connection.commit()
    except psycopg2.Error as e:
        print("Failed to create possible tables:", e)
    finally:
        cursor.close()
        connection.close()
# Call the function to check the existence of the 'possible_fields' table and create it if it doesn't exist
create_possible_fields_tables()

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
@app.route('/api/servers', methods=['POST'])
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

   
    try:
        # Check if possible_solution, possible_environment, possible_os, possible_tags, possible_system are exist
        for table in ("environment", "solution", "system", "os", "tags"):
            cursor.execute(
                f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'possible_{table}')"
            )
            table_exists = cursor.fetchone()[0]
            if not table_exists:
                # If the possible_fields table doesn't exist, return an error response
                return jsonify(message="Table possible_{table} does not exist"), 500

        # Check each field separately
        for field in ("environment", "solution", "system", "os"):
            if field in data:
                # Perform the check for non-empty value
                if not data[field]:
                    return jsonify(message=f"Field '{field}' cannot be empty. At least you need to assign the value 'unknown'."), 400

                # Perform the check against possible_fields table
                cursor.execute(
                    f"SELECT EXISTS (SELECT FROM possible_{field} WHERE {field} = %s)",
                    (data[field],)
                )
                value_exists = cursor.fetchone()[0]
                if not value_exists:
                    return jsonify(message=f"Invalid value '{data[field]}' for field '{field}'"), 400
                
        # Check the 'tags' field if it exists
        if 'tags' in data:
            tags = data['tags']
            if not isinstance(tags, list):
                return jsonify(message="Field 'tags' must be an array"), 400

            # Perform the check against possible_fields table for each tag
            for tag in tags:
                # Perform the check for non-empty value
                if not tag:
                    return jsonify(message="Tags cannot be empty. At least you need to assign the value 'unknown'."), 400

                # Perform the check against possible_fields table
                cursor.execute(
                    "SELECT EXISTS (SELECT FROM possible_tags WHERE tags = %s)",
                    (tag,)
                )

                value_exists = cursor.fetchone()[0]
                if not value_exists:
                    return jsonify(message=f"Invalid tag '{tag}'"), 400

        # Create a new record in the table
        cursor.execute(
            '''
            INSERT INTO servers (hostname, environment, solution, system, os, tags)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''',
            (hostname, data.get('environment'), data.get('solution'), data.get('system'), data.get('os'), data.get('tags'))
        )
        connection.commit()

        return jsonify({'message': 'Server created successfully'}), 201

    except psycopg2.Error as e:
        print("Error creating server:", e)
        return jsonify(message="Failed to create server: {}".format(str(e))), 500


    finally:
        cursor.close()
        connection.close()

# Route to update server by hostname
@app.route('/api/servers/<hostname>', methods=['PUT'])
def update_server_by_hostname(hostname):
    # Get the request data
    data = request.get_json()

    # Connect to the database
    connection = create_connection()
    cursor = connection.cursor()

    # Check if a record with the given hostname already exists
    cursor.execute('SELECT * FROM servers WHERE hostname = %s', (hostname,))
    if not cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify(message="Server with the given hostname does not exist"), 409
    
    try:
        # Check if possible_solution, possible_environment, possible_os, possible_tags, possible_system are exist
        for table in ("environment", "solution", "system", "os", "tags"):
            cursor.execute(
                f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'possible_{table}')"
            )
            table_exists = cursor.fetchone()[0]
            if not table_exists:
                # If the possible_fields table doesn't exist, return an error response
                return jsonify(message="Table possible_{table} does not exist"), 500

        # Check each field separately
        for field in ("environment", "solution", "system", "os"):
            if field in data:
                # Perform the check for non-empty value
                if not data[field]:
                    return jsonify(message=f"Field '{field}' cannot be empty. At least you need to assign the value 'unknown'."), 400

                # Perform the check against possible_fields table
                cursor.execute(
                    f"SELECT EXISTS (SELECT FROM possible_{field} WHERE {field} = %s)",
                    (data[field],)
                )
                value_exists = cursor.fetchone()[0]
                if not value_exists:
                    return jsonify(message=f"Invalid value '{data[field]}' for field '{field}'"), 400
                
                
        # Check the 'tags' field if it exists
        if 'tags' in data:
            tags = data['tags']
            if not isinstance(tags, list):
                return jsonify(message="Field 'tags' must be an array"), 400

            # Perform the check against possible_fields table for each tag
            for tag in tags:
                # Perform the check for non-empty value
                if not tag:
                    return jsonify(message="Tags cannot be empty. At least you need to assign the value 'unknown'."), 400

                # Perform the check against possible_fields table
                cursor.execute(
                    f"SELECT EXISTS (SELECT FROM possible_tags WHERE tags = %s)",
                    (tag,)
                )

                value_exists = cursor.fetchone()[0]
                if not value_exists:
                    return jsonify(message=f"Invalid tag '{tag}'"), 400

        # Update the server record in the database
        cursor.execute(
            """
            UPDATE servers
            SET environment = %s,
                solution = %s,
                system = %s,
                os = %s,
                tags = %s
            WHERE hostname = %s
            """,
            (data.get('environment'), data.get('solution'), data.get('system'), data.get('os'), data.get('tags'), hostname)
        )
        connection.commit()

        return jsonify(message="Server updated successfully"), 200

    except psycopg2.Error as e:
        print("Error updating server:", e)
        return jsonify(message="Failed to update server: {}".format(str(e))), 500


    finally:
        cursor.close()
        connection.close()

# Route to delete server by hostname
@app.route('/api/servers/<hostname>', methods=['DELETE'])
def delete_server_by_hostname(hostname):
    # Connect to the database
    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM servers WHERE hostname = %s", (hostname,))
        connection.commit()
        return jsonify({"message": "Deleted server successfully"})
    except psycopg2.Error as e:
        return jsonify({"message": "Failed to delete server", "error": str(e)}), 500
    
    finally:
        cursor.close()
        connection.close()

# Route to get all possible fields
@app.route('/api/fields', methods=['GET'])
def get_possible_fields1():
    try:
        connection = create_connection()
        cursor = connection.cursor()
        field_list = {}
        
        for table in ("environment", "solution", "system", "os", "tags"):
            query = f"SELECT * FROM possible_{table}"
            cursor.execute(query)
            possible_fields = cursor.fetchall()
            
            field_values = [field[0] for field in possible_fields]
            field_list[table] = field_values
        
        cursor.close()
        connection.close()
        
        return jsonify(field_list)
    
    except psycopg2.Error as e:
        return jsonify({"message": "Failed to retrieve possible fields", "error": str(e)}), 500

# Route to create solution
@app.route("/api/fields/solution", methods=["POST"])
def create_possible_solution():
    connection = create_connection()
    cursor = connection.cursor()
    try:
        data = request.get_json()
        solution = data.get("solution")

        cursor.execute("INSERT INTO possible_solution (solution) VALUES (%s)", (solution,))
        connection.commit()

        return jsonify({"message": "Created possible_solution successfully"})
    except psycopg2.Error as e:
        return jsonify({"message": "Failed to create possible_solution", "error": str(e)}), 500

# Route to create environment
@app.route("/api/fields/environment", methods=["POST"])
def create_possible_environment():
    connection = create_connection()
    cursor = connection.cursor()
    try:
        data = request.get_json()
        environment = data.get("environment")

        cursor.execute("INSERT INTO possible_environment (environment) VALUES (%s)", (environment,))
        connection.commit()

        return jsonify({"message": "Created possible_environment successfully"})
    except psycopg2.Error as e:
        return jsonify({"message": "Failed to create possible_environment", "error": str(e)}), 500

# Маршрут для создания записи в таблице possible_os
@app.route("/api/fields/os", methods=["POST"])
def create_possible_os():
    connection = create_connection()
    cursor = connection.cursor()
    try:
        data = request.get_json()
        os = data.get("os")

        cursor.execute("INSERT INTO possible_os (os) VALUES (%s)", (os,))
        connection.commit()

        return jsonify({"message": "Created possible_os successfully"})
    except psycopg2.Error as e:
        return jsonify({"message": "Failed to create possible_os", "error": str(e)}), 500

# Маршрут для создания записи в таблице possible_tags
@app.route("/api/fields/tags", methods=["POST"])
def create_possible_tags():
    connection = create_connection()
    cursor = connection.cursor()
    try:
        data = request.get_json()
        tags = data.get("tags")

        cursor.execute("INSERT INTO possible_tags (tags) VALUES (%s)", (tags,))
        connection.commit()

        return jsonify({"message": "Created possible_tags successfully"})
    except psycopg2.Error as e:
        return jsonify({"message": "Failed to create possible_tags", "error": str(e)}), 500

# Маршрут для создания записи в таблице possible_system
@app.route("/api/fields/system", methods=["POST"])
def create_possible_system():
    connection = create_connection()
    cursor = connection.cursor()
    try:
        data = request.get_json()
        system = data.get("system")

        cursor.execute("INSERT INTO possible_system (system) VALUES (%s)", (system,))
        connection.commit()

        return jsonify({"message": "Created possible_system successfully"})
    except psycopg2.Error as e:
        return jsonify({"message": "Failed to create possible_system", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
