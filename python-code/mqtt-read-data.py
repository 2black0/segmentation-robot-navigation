import time
import csv
import paho.mqtt.client as mqtt

# MQTT Broker
MQTT_BROKER = "192.168.100.27"
MQTT_PORT = 1883
MQTT_TOPICS = [
    "TurnValue",
    "ThrottleValue",
    "SafetyValue",
    "ModeValue",
    "ForwardValue",
    "StatusValue"
]  # Daftar topik yang akan disubscribe

# File CSV untuk menyimpan data
CSV_FILE = "motor_data.csv"

# Variabel global untuk menyimpan data dari topik MQTT
mqtt_data = {
    "TurnValue": 0,
    "ThrottleValue": 0,
    "SafetyValue": 0,
    "ModeValue": 0,
    "ForwardValue": 0,
    "StatusValue": 0
}

# Fungsi untuk menulis data ke file CSV
def write_to_csv():
    try:
        with open(CSV_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            row = [timestamp] + [mqtt_data[key] for key in MQTT_TOPICS]
            writer.writerow(row)
            print(f"Data written to CSV: {row}")
    except Exception as e:
        print(f"Error writing to CSV: {e}")

# Fungsi untuk menerima data MQTT
def on_message(client, userdata, message):
    try:
        # Mendapatkan nilai dari pesan MQTT
        topic = message.topic
        payload = int(message.payload.decode("utf-8"))

        if topic in mqtt_data:
            mqtt_data[topic] = payload
            print(f"Received from MQTT: {topic} = {payload}")

        # Simpan data ke file CSV
        write_to_csv()

    except Exception as e:
        print(f"Error processing MQTT message: {e}")

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        # Subscribe ke semua topik
        for topic in MQTT_TOPICS:
            client.subscribe(topic)
            print(f"Subscribed to {topic}")
    else:
        print(f"Failed to connect, return code {rc}")

# MQTT on_publish callback
def on_publish(client, userdata, mid):
    print(f"Message {mid} successfully published.")

# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

try:
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()  # Start MQTT loop
except Exception as e:
    print(f"Error connecting to MQTT broker: {e}")
    exit(1)

# Create the CSV file and write the header if it doesn't exist
try:
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp"] + MQTT_TOPICS)
        print(f"CSV file {CSV_FILE} created with headers.")
except Exception as e:
    print(f"Error creating CSV file: {e}")
    exit(1)

# Loop untuk menjalankan program (tanpa RTSP)
print("Running MQTT data logger. Press Ctrl+C to exit.")
try:
    while True:
        time.sleep(1)  # Program berjalan terus-menerus, menunggu data MQTT
except KeyboardInterrupt:
    print("\nProgram terminated.")
    client.loop_stop()
    client.disconnect()