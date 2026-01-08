from flask import Flask, request, jsonify
import sqlite3
import json
import paho.mqtt.client as mqtt
from datetime import datetime

# ---- CONFIG MQTT ----
MQTT_BROKER = "10.63.96.14"
MQTT_PORT = 1883
MQTT_TOPIC = "iot/mesures"

# ---- CONFIG SQLITE (cache) ----
DB_PATH = "mesures_cache.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS mesures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    temperature REAL,
    humidite REAL,
    gaz REAL,
    date TEXT,
    heure TEXT,
    latitude REAL,
    longitude REAL,
    deviceId TEXT,
    source TEXT
)
""")
conn.commit()

# ---- INIT MQTT ----
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# ---- FLASK SERVER ----
app = Flask(__name__)

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    now = datetime.now()
    timestamp = now.isoformat(timespec="seconds")
    date = now.strftime("%Y-%m-%d")
    heure = now.strftime("%H:%M:%S")

    # Extraction des champs envoyés
    deviceId = data.get("deviceId", "ESP8266_01")
    temperature = data.get("temperature")
    humidite = data.get("humidite")
    gaz = data.get("gaz")
    latitude = data.get("latitude", 0.0)
    longitude = data.get("longitude", 0.0)

    # ---- Insert SQLite ----
    cur.execute("""
        INSERT INTO mesures (timestamp, temperature, humidite, gaz, date, heure, latitude, longitude, deviceId, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (timestamp, temperature, humidite, gaz, date, heure, latitude, longitude, deviceId, "wifi_gateway")
    )
    conn.commit()

    # ---- Publish to MQTT ----
    payload = {
        "deviceId": deviceId,
        "temperature": temperature,
        "humidite": humidite,
        "gaz": gaz,
        "date": date,
        "heure": heure,
        "latitude": latitude,
        "longitude": longitude
    }

    client.publish(MQTT_TOPIC, json.dumps(payload))

    print("MQTT publié:", payload)

    return jsonify({"status": "OK", "mqtt": "published", "data_saved": True})

if __name__ == "__main__":
    print("Gateway WiFi démarrée sur port 5000...")
    app.run(host="0.0.0.0", port=5000)
