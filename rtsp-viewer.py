#!/usr/bin/env python -c

# Import OpenCV and threading packages
import cv2
import threading

# Define class for the camera thread.
class CamThread(threading.Thread):

    def __init__(self, previewname, camid):
        threading.Thread.__init__(self)
        self.previewname = previewname
        self.camid = camid

    def run(self):
        print("Starting " + self.previewname)
        previewcam(self.previewname, self.camid)

# Function to preview the camera.
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
        if key == 27:  # Press ESC to exit/close each window.
            break
    cv2.destroyWindow(previewname)

# Create different threads for each video stream, then start it.
thread1 = CamThread("FrontCamera", 'rtsp://192.168.100.47:8554/cam')
#thread2 = CamThread("Front Door", 'rtsp://username:SuperSecurePassword@192.168.1.2/Streaming/Channels/202')
#thread3 = CamThread("Garage", 'rtsp://username:SuperSecurePassword@192.168.1.2/Streaming/Channels/302')
thread1.start()
#thread2.start()
#thread3.start()

# check out tutorials point link below for multi-threading sample
# https://www.tutorialspoint.com/python/python_multithreading.htm