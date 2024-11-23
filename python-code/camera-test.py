import numpy as np
import cv2

#cap = cv2.VideoCapture(0) // for usb camera
cap = cv2.VideoCapture('http://192.168.100.27:4747/video')

while(True):
    ret, frame = cap.read()
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    cv2.imshow('frame',frame)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()