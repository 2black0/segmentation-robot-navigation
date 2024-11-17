import cv2
import threading
import time
import paho.mqtt.client as mqtt

# MQTT Broker
MQTT_BROKER = "192.168.100.27"
MQTT_PORT = 1883
MQTT_TOPIC_RIGHT = "MotorKanan"
MQTT_TOPIC_LEFT = "MotorKiri"

# Interval pengiriman data dalam detik
SEND_INTERVAL = 1

# Variabel global untuk mencatat waktu pengiriman terakhir
last_send_time = 0

# Fungsi untuk mengirimkan data ke MQTT broker
def send_speed_data(right_speed, left_speed):
    try:
        # Kirim data dengan QoS 1 untuk memastikan penerimaan
        result_right = client.publish(MQTT_TOPIC_RIGHT, right_speed, qos=1)
        result_left = client.publish(MQTT_TOPIC_LEFT, left_speed, qos=1)
        
        # Periksa hasil pengiriman
        if result_right.rc == 0 and result_left.rc == 0:
            print(f"Data sent via MQTT: RightSpeed = {right_speed}, LeftSpeed = {left_speed}")
        else:
            print("Failed to send data. MQTT client returned an error.")
    except Exception as e:
        print(f"Error sending data via MQTT: {e}")

# Define class for the camera thread
class CamThread(threading.Thread):
    def __init__(self, previewname, camid):
        threading.Thread.__init__(self)
        self.previewname = previewname
        self.camid = camid

    def run(self):
        print("Starting " + self.previewname)
        previewcam(self.previewname, self.camid)

# Function to preview the camera
def previewcam(previewname, camid):
    global last_send_time
    cv2.namedWindow(previewname)
    cam = cv2.VideoCapture(camid)
    if cam.isOpened():
        rval, frame = cam.read()
    else:
        rval = False

    while rval:
        cv2.imshow(previewname, frame)
        rval, frame = cam.read()
        key = cv2.waitKey(20)
        
        # Periksa apakah waktu pengiriman berikutnya sudah tercapai
        current_time = time.time()
        if current_time - last_send_time >= SEND_INTERVAL:
            # Mengirimkan data kecepatan motor
            RightSpeed = 40  # Kecepatan tetap (atau gunakan nilai dinamis sesuai kebutuhan)
            LeftSpeed = 40
            threading.Thread(target=send_speed_data, args=(RightSpeed, LeftSpeed)).start()
            last_send_time = current_time  # Perbarui waktu pengiriman terakhir
        
        # Menampilkan perubahan data di konsol
        #print(f"Previewing video: {previewname}")

        if key == 27:  # Tekan ESC untuk keluar dan menutup jendela
            break
    cv2.destroyWindow(previewname)

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

# MQTT on_publish callback
def on_publish(client, userdata, mid):
    print(f"Message {mid} successfully published.")

# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish  # Callback untuk memverifikasi pengiriman

try:
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()  # Start MQTT loop
except Exception as e:
    print(f"Error connecting to MQTT broker: {e}")
    exit(1)

# Create different threads for each video stream, then start it
thread1 = CamThread("FrontCamera", 'rtsp://camera:CAMera123@192.168.115.7/live/ch00_1')
thread1.start()