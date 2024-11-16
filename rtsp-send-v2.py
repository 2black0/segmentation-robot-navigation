import cv2
import threading
import requests
import time

# Server URL untuk mengirimkan data kecepatan motor kanan dan kiri
SERVER_URL = "http://192.168.115.24/setSpeed"  # IP ESP32

# Interval pengiriman data dalam detik
SEND_INTERVAL = 1

# Variabel global untuk mencatat waktu pengiriman terakhir
last_send_time = 0

# Fungsi untuk mengirimkan data ke server dengan verifikasi
def send_speed_data(right_speed, left_speed):
    try:
        # Mengirimkan data ke server
        response = requests.get(SERVER_URL, params={'RightSpeed': right_speed, 'LeftSpeed': left_speed}, timeout=2)
        if response.status_code == 200:
            # Verifikasi respons dari server
            print(f"Data sent successfully: RightSpeed = {right_speed}, LeftSpeed = {left_speed}")
        else:
            print(f"Failed to send data. HTTP status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data: {e}")

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
        print(f"Previewing video: {previewname}")

        if key == 27:  # Tekan ESC untuk keluar dan menutup jendela
            break
    cv2.destroyWindow(previewname)

# Create different threads for each video stream, then start it
thread1 = CamThread("FrontCamera", 'rtsp://camera:CAMera123@192.168.115.7/live/ch00_1')
thread1.start()
