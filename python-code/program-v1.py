import cv2
import numpy as np
import time
import logging
from ultralytics import YOLO

# Suppress YOLO debug outputs
logging.getLogger("ultralytics").setLevel(logging.ERROR)


class ROICenterlineProcessor:
    def __init__(self, rtsp_url, model_path, active_rois, Kp, Ki, Kd, base_speed):
        """
        Initialize the ROICenterlineProcessor with RTSP URL, YOLO model, and active ROIs.

        Args:
            rtsp_url (str): URL of the RTSP stream.
            model_path (str): Path to the YOLO model file.
            active_rois (list of int): List of ROI indices to activate.
            Kp, Ki, Kd (float): PID controller gains.
            base_speed (int): Base speed for motors.
        """
        self.rtsp_url = rtsp_url
        self.cap = cv2.VideoCapture(rtsp_url)
        if not self.cap.isOpened():
            raise ValueError(f"Unable to connect to RTSP stream: {rtsp_url}")
        self.model = YOLO(model_path)
        self.active_rois = active_rois
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.base_speed = base_speed
        self.prev_error = 0
        self.integral = 0
        self.last_time = time.time()

    def process_segmentation(self, frame):
        """
        Perform YOLO instance segmentation on the frame and create a binary mask.

        Args:
            frame (numpy.ndarray): The input video frame.

        Returns:
            tuple: (annotated_frame, binary_mask_frame)
                   - annotated_frame: Frame with YOLO annotations.
                   - binary_mask_frame: Binary mask frame (white for segmented regions, black for background).
        """
        results = self.model(frame)
        result = results[0]

        # Generate annotated frame
        annotated_frame = result.plot()

        # Create binary mask
        height, width = frame.shape[:2]
        binary_mask_frame = np.zeros((height, width, 3), dtype=np.uint8)

        if result.masks is not None:
            mask = np.zeros((height, width), dtype=np.uint8)
            for seg in result.masks.data:
                seg = seg.cpu().numpy()
                seg = (seg > 0.5).astype(np.uint8)
                mask = cv2.bitwise_or(mask, seg)

            binary_mask_frame = cv2.merge([mask * 255] * 3)

        return annotated_frame, binary_mask_frame

    def calculate_roi_midpoints(self, binary_mask):
        """
        Calculate midpoints for the active ROIs.

        Args:
            binary_mask (numpy.ndarray): Binary mask frame (white for segmented regions, black for background).

        Returns:
            dict: Dictionary of midpoints for active ROIs with ROI index as the key.
        """
        gray_mask = cv2.cvtColor(binary_mask, cv2.COLOR_BGR2GRAY)
        height, width = gray_mask.shape
        roi_height = height // 10

        midpoints = {}

        for roi_index in self.active_rois:
            start_y = roi_index * roi_height
            end_y = (roi_index + 1) * roi_height
            roi = gray_mask[start_y:end_y, :]

            edges = cv2.Canny(roi, threshold1=50, threshold2=150)

            rows, cols = roi.shape
            left, right = None, None
            for y in range(rows):
                edge_indices = np.where(edges[y, :] > 0)[0]
                if len(edge_indices) >= 2:
                    left = edge_indices[0]
                    right = edge_indices[-1]
                    break

            if left is not None and right is not None:
                midpoint_x = (left + right) // 2
                midpoint_y = start_y + roi_height // 2
                midpoints[roi_index] = (midpoint_x, midpoint_y)
            else:
                midpoints[roi_index] = None

        return midpoints

    def detect_straight_path(self, midpoints):
        """
        Detect whether the path is straight based on active ROI midpoints.

        Args:
            midpoints (dict): Dictionary of midpoints for active ROIs.

        Returns:
            bool: True if the path is straight, False otherwise.
        """
        x_coords = [midpoints[roi][0] for roi in midpoints if midpoints[roi] is not None]
        if len(x_coords) < 2:
            return True  # Not enough data to determine, assume straight

        deviations = [abs(x - x_coords[0]) for x in x_coords]
        return max(deviations) <= 50  # Threshold for straightness

    def calculate_pid_correction(self, error):
        """
        Calculate the PID correction value based on the error.

        Args:
            error (float): The current error value.

        Returns:
            float: PID correction value.
        """
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0
        self.prev_error = error

        correction = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        return correction

    def process_stream(self):
        """
        Process the RTSP stream with YOLO segmentation and display the results.
        """
        frame_center_x = 320  # Assuming a frame width of 640
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            annotated_frame, binary_mask_frame = self.process_segmentation(frame)
            midpoints = self.calculate_roi_midpoints(binary_mask_frame)

            # Detect straight path or not
            is_straight = self.detect_straight_path(midpoints)
            path_type = "Straight" if is_straight else "Not Straight"

            # Use the bottom-most ROI for error calculation
            if midpoints:
                bottom_roi = max(midpoints.keys())
                if midpoints[bottom_roi] is not None:
                    midpoint_x = midpoints[bottom_roi][0]
                    error = midpoint_x - frame_center_x

                    # Calculate PID correction
                    correction = self.calculate_pid_correction(error)

                    # Calculate motor speeds
                    left_speed = self.base_speed - correction
                    right_speed = self.base_speed + correction

                    # Print all relevant values in one line
                    print(f"{path_type} | Error: {error:.2f} | Correction: {correction:.2f} | "
                          f"Left Speed: {left_speed:.2f} | Right Speed: {right_speed:.2f}")

                    # Draw ROI midpoint
                    cv2.circle(frame, (midpoint_x, int((bottom_roi + 0.5) * (frame.shape[0] // 10))), 5, (0, 255, 0), -1)

            # Draw ROI boxes
            height, width = frame.shape[:2]
            roi_height = height // 10

            for roi_index in range(10):
                start_y = roi_index * roi_height
                end_y = (roi_index + 1) * roi_height
                color = (255, 0, 0) if roi_index in self.active_rois else (100, 100, 100)
                thickness = 2 if roi_index in self.active_rois else 1
                cv2.rectangle(frame, (0, start_y), (width, end_y), color, thickness)

            # Display the frames
            cv2.imshow('YOLO Annotated Frame', annotated_frame)
            cv2.imshow('Binary Segmentation Mask', binary_mask_frame)
            cv2.imshow('ROI Midpoints', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cleanup()

    def cleanup(self):
        """
        Release resources and close display windows.
        """
        self.cap.release()
        cv2.destroyAllWindows()


# Usage example
if __name__ == "__main__":
    rtsp_url = 'http://192.168.100.27:4747/video'
    model_path = 'python-code/yolo11s-seg-v1-train10.pt'
    active_rois = [2, 5, 7]  # Active ROIs: 2, 5, and 7
    base_speed = 30
    Kp, Ki, Kd = 0.1, 0.0, 0.0  # PID gains

    try:
        roi_processor = ROICenterlineProcessor(rtsp_url, model_path, active_rois, Kp, Ki, Kd, base_speed)
        roi_processor.process_stream()
    except Exception as e:
        print(f"Error: {e}")