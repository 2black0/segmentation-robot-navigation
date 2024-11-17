import cv2
import threading
import time
import numpy as np
import paho.mqtt.client as mqtt

# MQTT Broker
MQTT_BROKER = "192.168.100.27"
MQTT_PORT = 1883
MQTT_TOPIC_RIGHT = "MotorKanan"
MQTT_TOPIC_LEFT = "MotorKiri"

# Kendali
SEND_INTERVAL = 0.1  # Interval pengiriman data ke MQTT dalam detik
KP = 0.5             # Koefisien kendali proporsional
CONTROL_MIN = 20     # Batas minimal kecepatan motor
CONTROL_MAX = 100    # Batas maksimal kecepatan motor

# Variabel global
last_send_time = 0
frame_width = 640  # Asumsi lebar frame video
frame_height = 480  # Asumsi tinggi frame video
crop_height = 50    # Tinggi crop horizontal
num_section = 1     # Fokus hanya pada satu bagian horizontal

# MQTT setup
def setup_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
    except Exception as e:
        print(f"Error connecting to MQTT broker: {e}")
        exit(1)
    return client

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message {mid} successfully published.")

# Fungsi untuk mengirimkan data ke MQTT broker
def send_speed_data(client, right_speed, left_speed):
    try:
        result_right = client.publish(MQTT_TOPIC_RIGHT, right_speed, qos=1)
        result_left = client.publish(MQTT_TOPIC_LEFT, left_speed, qos=1)
        if result_right.rc == 0 and result_left.rc == 0:
            print(f"Data sent via MQTT: RightSpeed = {right_speed}, LeftSpeed = {left_speed}")
        else:
            print("Failed to send data. MQTT client returned an error.")
    except Exception as e:
        print(f"Error sending data via MQTT: {e}")

# Fungsi untuk memproses frame dan mendeteksi garis hitam
def process_frame(frame, client):
    global last_send_time

    # Konversi ke grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Otsu's thresholding untuk mendapatkan binary image
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Bagian horizontal untuk deteksi
    y_start = frame_height - crop_height
    y_end = frame_height
    crop = binary[y_start:y_end, :]
    
    # Overlay bounding box pada area crop
    cv2.rectangle(frame, (0, y_start), (frame_width, y_end), (0, 255, 0), 2)

    # Deteksi posisi garis hitam menggunakan moments
    moments = cv2.moments(crop)
    if moments["m00"] > 0:
        center_x = int(moments["m10"] / moments["m00"])
        cv2.circle(frame, (center_x, y_start + crop_height // 2), 5, (0, 0, 255), -1)
    else:
        center_x = frame_width // 2  # Default ke tengah jika tidak terdeteksi

    # Kendali proporsional berdasarkan nilai tengah
    error = frame_width // 2 - center_x
    control = KP * error
    right_speed = int(np.clip(CONTROL_MIN + control, CONTROL_MIN, CONTROL_MAX))
    left_speed = int(np.clip(CONTROL_MIN - control, CONTROL_MIN, CONTROL_MAX))

    # Kirim data kecepatan motor jika interval tercapai
    current_time = time.time()
    if current_time - last_send_time >= SEND_INTERVAL:
        send_speed_data(client, right_speed, left_speed)
        last_send_time = current_time

    return frame

# Fungsi untuk menampilkan video dan menjalankan deteksi
def preview_camera(camid, client):
    cap = cv2.VideoCapture(camid)
    if not cap.isOpened():
        print("Error: Camera not accessible")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = process_frame(frame, client)
        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) == 27:  # Tekan ESC untuk keluar
            break

    cap.release()
    cv2.destroyAllWindows()

# Thread kamera
class CameraThread(threading.Thread):
    def __init__(self, camid, client):
        threading.Thread.__init__(self)
        self.camid = camid
        self.client = client

    def run(self):
        preview_camera(self.camid, self.client)

# Main program
if __name__ == "__main__":
    client = setup_mqtt()
    rtsp_url = 'rtsp://camera:CAMera123@192.168.115.7/live/ch00_1'
    camera_thread = CameraThread(rtsp_url, client)
    camera_thread.start()