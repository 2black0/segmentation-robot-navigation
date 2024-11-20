import cv2
import numpy as np
from ultralytics import YOLO

class RobotNavigation:
    def __init__(self, ImagePath, ModelPath="python-code\\model-v1.pt", TotalSections=10, ActiveSections=None):
        """
        Initialize the robot with an image source and YOLO model for segmentation.
        :param ImagePath: Path to the image file (e.g., 'path/to/image.jpg').
        :param ModelPath: Path to the YOLOv11 model file for instance segmentation.
        :param TotalSections: Total number of horizontal sections to divide the frame.
        :param ActiveSections: Specific sections that will be highlighted.
        """
        self.ImagePath = ImagePath
        self.Model = YOLO(ModelPath)
        self.TotalSections = TotalSections
        self.SectionHeight = None  # To be defined based on image dimensions
        self.ActiveSections = ActiveSections if ActiveSections is not None else list(range(1, TotalSections + 1))

    def DrawSections(self, Frame):
        if self.SectionHeight is None:  # Calculate section height based on the actual image dimensions
            self.FrameHeight, self.FrameWidth = Frame.shape[:2]
            self.SectionHeight = self.FrameHeight // self.TotalSections

        CenterX = self.FrameWidth // 2
        for Section in self.ActiveSections:
            YStart = self.FrameHeight - (Section * self.SectionHeight)
            YEnd = YStart + self.SectionHeight
            cv2.rectangle(Frame, (0, YStart), (self.FrameWidth, YEnd), (255, 0, 0), 2)
        cv2.line(Frame, (CenterX, 0), (CenterX, self.FrameHeight), (0, 255, 0), 2)
        return Frame

    def DrawDetections(self, Frame, Results):
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Define colors for different classes
        for result in Results:
            for i, det in enumerate(result.boxes.xyxy):
                x1, y1, x2, y2 = map(int, det)
                color = colors[int(result.boxes.cls[i] % len(colors))]
                cv2.rectangle(Frame, (x1, y1), (x2, y2), color, 2)  # Draw rectangle around detected object
                label = f'{result.boxes.cls[i]:.0f}: {result.boxes.conf[i]:.2f}'
                cv2.putText(Frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return Frame

    def Run(self):
        Frame = cv2.imread(self.ImagePath)
        if Frame is None:
            print("Error: Image not accessible")
            return

        Frame = cv2.resize(Frame, (640, 480))  # Resize to standard dimensions if necessary

        # Process instance segmentation using YOLO
        Results = self.Model.predict(Frame)
        SegmentedFrame = self.DrawDetections(Frame.copy(), Results)

        # Draw active sections on the frame
        ProcessedFrame = self.DrawSections(SegmentedFrame)

        cv2.imshow("Processed Frame with Active Sections and Instance Segmentation", ProcessedFrame)
        cv2.waitKey(0)  # Wait indefinitely until a key is pressed

        cv2.destroyAllWindows()

if __name__ == "__main__":
    ImagePath = "python-code\gambar2.jpg"  # Specify the path to your JPEG image
    ModelPath = "python-code\\model-v1.pt"  # Adjust according to your model file path
    Robot = RobotNavigation(ImagePath, ModelPath, TotalSections=10, ActiveSections=[2, 7])
    Robot.Run()