from ultralytics import YOLO
import cv2

model = YOLO('python-code/yolo11s-seg-v1-train10.pt')
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture('http://192.168.100.27:4747/video')

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break  

    results = model(frame)
    result = results[0]

    annotated_frame = result.plot()
    #annotated_frame = cv2.rotate(annotated_frame, cv2.ROTATE_90_CLOCKWISE)
    cv2.imshow('YOLO Inference', annotated_frame)
    
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()