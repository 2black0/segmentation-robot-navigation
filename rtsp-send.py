import cv2
import threading
import requests
import time
import random  # Untuk menghasilkan angka acak

# Server URL untuk mengirimkan data kecepatan motor kanan dan kiri
SERVER_URL = "http://192.168.115.24/setSpeed"  # Menggunakan IP ESP32 Anda yang baru

# Fungsi untuk mengirimkan data kecepatan ke server
def send_speed_data(right_speed, left_speed):
    try:
        # Mengirimkan data kecepatan melalui HTTP GET request
        response = requests.get(SERVER_URL, params={'RightSpeed': right_speed, 'LeftSpeed': left_speed})
        if response.status_code == 200:
            print(f"Data sent successfully: RightSpeed = {right_speed}, LeftSpeed = {left_speed}")
        else:
            print(f"Failed to send data: {response.status_code}")
    except Exception as e:
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
        
        # Menghasilkan kecepatan acak untuk motor kanan dan kiri
        RightSpeed = 40 #random.randint(0, 255)  # Nilai acak untuk kecepatan motor kanan (0-255)
        LeftSpeed = 40 #random.randint(0, 255)   # Nilai acak untuk kecepatan motor kiri (0-255)
        
        # Kirimkan data kecepatan motor setiap detik
        send_speed_data_periodically(RightSpeed, LeftSpeed)
        
        # Menampilkan perubahan data setiap kali frame diperbarui
        print(f"Sending: RightSpeed = {RightSpeed}, LeftSpeed = {LeftSpeed}")
        
        if key == 27:  # Press ESC to exit/close each window.
            break
    cv2.destroyWindow(previewname)

# Fungsi untuk mengirimkan data setiap 1 detik
def send_speed_data_periodically(right_speed, left_speed):
    def send_data():
        threading.Thread(target=send_speed_data, args=(right_speed, left_speed)).start()
    
    # Mengirim data pertama kali
    send_data()
    
    # Mengatur pengiriman data per 1 detik
    threading.Timer(1, send_speed_data_periodically, args=(right_speed, left_speed)).start()

# Create different threads for each video stream, then start it
thread1 = CamThread("FrontCamera", 'rtsp://camera:CAMera123@192.168.115.7/live/ch00_1')
thread1.start()