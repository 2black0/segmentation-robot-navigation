import cv2
import numpy as np
from ultralytics import YOLO

class ROICenterlineProcessor:
    def __init__(self, rtsp_url, model_path, active_rois):
        """
        Initialize the ROICenterlineProcessor with RTSP URL, YOLO model, and active ROIs.

        Args:
            rtsp_url (str): URL of the RTSP stream.
            model_path (str): Path to the YOLO model file.
            active_rois (list of int): List of ROI indices to activate.
        """
        self.rtsp_url = rtsp_url
        self.cap = cv2.VideoCapture(rtsp_url)
        if not self.cap.isOpened():
            raise ValueError(f"Unable to connect to RTSP stream: {rtsp_url}")
        self.model = YOLO(model_path)
        self.active_rois = active_rois  # List of active ROI indices

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

        # Create binary mask (black frame initially)
        height, width = frame.shape[:2]
        binary_mask_frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Process masks if available
        if result.masks is not None:
            mask = np.zeros((height, width), dtype=np.uint8)
            for seg in result.masks.data:  # Loop through segmentation masks
                seg = seg.cpu().numpy()  # Convert tensor to numpy array
                seg = (seg > 0.5).astype(np.uint8)  # Binarize mask
                mask = cv2.bitwise_or(mask, seg)

            # Convert mask to white (255) for segmented regions
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
        # Convert binary mask to grayscale
        gray_mask = cv2.cvtColor(binary_mask, cv2.COLOR_BGR2GRAY)

        # Define ROIs (divide the frame into 10 equal parts)
        height, width = gray_mask.shape
        roi_height = height // 10

        midpoints = {}

        for roi_index in self.active_rois:
            # Define the ROI
            start_y = roi_index * roi_height
            end_y = (roi_index + 1) * roi_height
            roi = gray_mask[start_y:end_y, :]

            # Detect edges in the ROI
            edges = cv2.Canny(roi, threshold1=50, threshold2=150)

            # Find leftmost and rightmost edges for the ROI
            rows, cols = roi.shape
            left, right = None, None
            for y in range(rows):
                edge_indices = np.where(edges[y, :] > 0)[0]
                if len(edge_indices) >= 2:
                    left = edge_indices[0]
                    right = edge_indices[-1]
                    break  # Take the first valid row

            if left is not None and right is not None:
                # Calculate the midpoint
                midpoint_x = (left + right) // 2
                midpoint_y = start_y + roi_height // 2  # ROI midpoint in the full frame
                midpoints[roi_index] = (midpoint_x, midpoint_y)
            else:
                # If no valid edges, add None
                midpoints[roi_index] = None

        return midpoints

    def process_stream(self):
        """
        Process the RTSP stream with YOLO segmentation and display the results.
        """
        print("Press 'q' to quit.")
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # Perform segmentation and generate binary mask
            annotated_frame, binary_mask_frame = self.process_segmentation(frame)

            # Calculate midpoints for the active ROIs
            midpoints = self.calculate_roi_midpoints(binary_mask_frame)

            # Draw midpoints and ROI boundaries on the frame
            height, width = frame.shape[:2]
            roi_height = height // 10

            for roi_index in range(10):  # Draw all ROIs
                start_y = roi_index * roi_height
                end_y = (roi_index + 1) * roi_height
                color = (255, 0, 0) if roi_index in self.active_rois else (100, 100, 100)
                cv2.rectangle(frame, (0, start_y), (width, end_y), color, 2)

                if roi_index in midpoints and midpoints[roi_index] is not None:
                    midpoint = midpoints[roi_index]
                    cv2.circle(frame, midpoint, 5, (0, 255, 0), -1)  # Green midpoint

            # Display the frames
            cv2.imshow('YOLO Annotated Frame', annotated_frame)
            cv2.imshow('Binary Segmentation Mask', binary_mask_frame)
            cv2.imshow('ROI Midpoints', frame)

            # Break the loop on 'q' key press
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
    try:
        roi_processor = ROICenterlineProcessor(rtsp_url, model_path, active_rois)
        roi_processor.process_stream()
    except Exception as e:
        print(f"Error: {e}")