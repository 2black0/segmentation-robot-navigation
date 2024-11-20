import cv2
import numpy as np

class LineFollowerRobot:
    def __init__(self, rtsp_url, total_sections=10, active_sections=None):
        # RTSP URL
        self.rtsp_url = rtsp_url

        # Frame parameters
        self.frame_width = 640
        self.frame_height = 480

        # Jumlah total bagian dan bagian aktif
        self.total_sections = total_sections
        self.section_height = self.frame_height // self.total_sections  # Tinggi setiap bagian = 48 px
        if active_sections is None:
            # Default ke semua bagian jika active_sections tidak diberikan
            self.active_sections = list(range(1, total_sections + 1))
        else:
            self.active_sections = active_sections

        # Rentang warna hitam dalam HSV
        self.lower_black = np.array([0, 0, 0])     # Rentang bawah warna hitam
        self.upper_black = np.array([180, 255, 50])  # Rentang atas warna hitam

    def draw_sections(self, frame):
        """Draw active sections on the frame with blue rectangles."""
        for section in self.active_sections:
            # Bagian dihitung dari bawah (1 = bagian paling bawah)
            y_start = self.frame_height - (section * self.section_height)
            y_end = y_start + self.section_height

            # Gambar kotak dengan garis biru
            cv2.rectangle(frame, (0, y_start), (self.frame_width, y_end), (255, 0, 0), 2)

        return frame

    def process_active_sections(self, frame):
        """Process only the active sections for black color detection using HSV."""
        mask = np.ones(frame.shape[:2], dtype="uint8") * 255  # Mask untuk bagian luar aktif
        overlay = frame.copy()  # Salinan frame untuk overlay

        # Konversi frame ke HSV
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        for section in self.active_sections:
            # Bagian dihitung dari bawah (1 = bagian paling bawah)
            y_start = self.frame_height - (section * self.section_height)
            y_end = y_start + self.section_height

            # Region of Interest (ROI) untuk bagian aktif
            roi = hsv_frame[y_start:y_end, :]

            # Mask untuk mendeteksi warna hitam
            black_mask = cv2.inRange(roi, self.lower_black, self.upper_black)

            # Tambahkan overlay warna hijau untuk area hitam yang terdeteksi
            overlay[y_start:y_end, :] = cv2.addWeighted(overlay[y_start:y_end, :], 0.7, 
                                                        np.dstack([black_mask] * 3), 0.3, 0)

            # Area aktif tetap pada frame utama, sisanya dibuat putih
            mask[y_start:y_end, :] = 0

        # Bagian di luar area aktif diubah menjadi putih
        frame[np.where(mask == 255)] = [255, 255, 255]

        # Kembali frame dengan overlay
        return frame

    def run(self):
        """Main loop for the robot."""
        cap = cv2.VideoCapture(self.rtsp_url)
        if not cap.isOpened():
            print("Error: Camera not accessible")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to capture frame")
                break

            # Resize frame untuk memastikan ukuran konsisten
            frame = cv2.resize(frame, (self.frame_width, self.frame_height), interpolation=cv2.INTER_LINEAR)

            # Frame Original dengan Kotak Biru
            original_frame = self.draw_sections(frame.copy())

            # Frame dengan Bagian Luar Putih dan Deteksi Warna Hitam
            processed_frame = self.process_active_sections(frame.copy())

            # Tampilkan hasil deteksi
            cv2.imshow("Original Frame with Active Sections", original_frame)
            cv2.imshow("Processed Frame with Black Detection (HSV)", processed_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Tekan 'q' untuk keluar
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Replace with your RTSP URL
    #rtsp_url = 'rtsp://camera:CAMera123@192.168.115.7/live/ch00_1'
    rtsp_url = 0
    # Konfigurasi total bagian dan bagian yang ingin di-overlay
    total_sections = 10
    active_sections = [2, 7]  # Bagian aktif: 2 dan 7

    robot = LineFollowerRobot(rtsp_url, total_sections=total_sections, active_sections=active_sections)
    robot.run()