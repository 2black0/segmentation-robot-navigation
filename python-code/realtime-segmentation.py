import cv2
from ultralytics import YOLO

# Load the YOLOv11 model (sesuaikan dengan path model Anda)
model_path = "python-code\model-v1.pt"  # Ganti dengan path model Anda
model = YOLO(model_path)

# Buka kamera USB
camera_id = 0  # Kamera default
cap = cv2.VideoCapture(camera_id)

if not cap.isOpened():
    print("Error: Tidak dapat mengakses kamera.")
    exit()

print("Tekan 'q' untuk keluar.")

while True:
    # Baca frame dari kamera
    ret, frame = cap.read()
    if not ret:
        print("Error: Tidak dapat membaca frame dari kamera.")
        break

    # Gunakan model untuk segmentasi real-time
    results = model.predict(source=frame, task='segment', verbose=False)

    # Ambil hasil segmentasi dari model
    segmented_frame = results[0].plot()  # Menambahkan hasil segmentasi pada frame

    # Tampilkan hasil segmentasi
    cv2.imshow("YOLOv11 Real-Time Segmentation", segmented_frame)

    # Tekan 'q' untuk keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Lepaskan kamera dan tutup semua jendela
cap.release()
cv2.destroyAllWindows()
