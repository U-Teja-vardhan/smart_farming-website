from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import openai
import os
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME")
}

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route("/api/register", methods=["POST"])
def register():
    conn = None
    cursor = None
    try:
        data = request.json
        username = data["username"]
        password = data["password"]
        role = data["role"]

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return jsonify({"message": "Username already exists. Please choose a different one."}), 409

        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
            (username, hashed_password, role)
        )
        conn.commit()
        return jsonify({"message": "Registered successfully"}), 201

    except Exception as e:
        print("Register error:", str(e))
        return jsonify({"message": "Registration failed"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password_hash'], password):
            return jsonify({'success': True, 'role': user['role'], 'username': user['username'], 'esp32_id': user['esp32_id']})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    finally:
        cursor.close()
        conn.close()

@app.route('/api/farmers', methods=['GET'])
def get_farmers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username FROM users WHERE role = 'farmer'")
    farmers = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(farmers)

@app.route('/api/send-request', methods=['POST'])
def send_request():
    data = request.get_json()
    customer_id = data['customer_id']
    farmer_id = data['farmer_id']
    quantity = data['quantity']
    price = data['price']
    requested_date = data['requested_date']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO requests (customer_id, farmer_id, quantity, price, requested_date) VALUES (%s, %s, %s, %s, %s)",
                       (customer_id, farmer_id, quantity, price, requested_date))
        conn.commit()
        return jsonify({'message': 'Request submitted successfully'}), 200
    except Error as e:
        return jsonify({'message': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/requests-received/<int:farmer_id>', methods=['GET'])
def get_requests(farmer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id, u.username AS customer_name, r.quantity, r.price, r.requested_date
        FROM requests r
        JOIN users u ON r.customer_id = u.id
        WHERE r.farmer_id = %s
    """, (farmer_id,))
    requests_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(requests_list)

@app.route('/api/sensor-data', methods=['POST'])
def store_sensor_data():
    data = request.get_json()
    esp32_id = data['esp32_id']
    temp = data['temperature']
    hum = data['humidity']
    ph = data['pH']
    tds = data['tds']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sensor_data (esp32_id, temperature, humidity, pH, tds)
        VALUES (%s, %s, %s, %s, %s)
    """, (esp32_id, temp, hum, ph, tds))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Sensor data stored successfully'}), 200

@app.route('/api/sensor-data/<esp32_id>', methods=['GET'])
def get_sensor_data(esp32_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sensor_data WHERE esp32_id = %s ORDER BY timestamp DESC LIMIT 100", (esp32_id,))
    sensor_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(sensor_data)

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    query = data['message']
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}],
            temperature=0.7,
            max_tokens=150
        )
        return jsonify({"response": response.choices[0].message['content']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
