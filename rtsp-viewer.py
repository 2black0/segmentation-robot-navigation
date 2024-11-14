import cv2
import threading

class CamThread(threading.Thread):
    def __init__(self, previewname, camid):
        threading.Thread.__init__(self)
        self.previewname = previewname
        self.camid = camid

    def run(self):
        print("Starting " + self.previewname)
        previewcam(self.previewname, self.camid)

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
        if frame is not None:
            # Convert the frame to HSV color space
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Define range of white color in HSV
            # Note: Adjust the range according to your lighting condition and the camera sensitivity
            lower_white = (0, 0, 200)   # Lower bound for HSV values for white color
            upper_white = (180, 55, 255) # Upper bound for HSV values for white color

            # Threshold the HSV image to get only white colors
            mask = cv2.inRange(hsv, lower_white, upper_white)

            # Find contours in the mask
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Draw bounding boxes for each detected object
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Show the frame with bounding boxes
            cv2.imshow(previewname, frame)

        key = cv2.waitKey(20)
        if key == 27:  # Press ESC to exit/close each window.
            break
    cv2.destroyWindow(previewname)

# Create different threads for each video stream, then start it.
thread1 = CamThread("FrontCamera", 'rtsp://192.168.115.117:8554/cam')
thread1.start()