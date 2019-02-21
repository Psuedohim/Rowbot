import cv2
import imutils
from imutils.video import WebcamVideoStream
from process_frame import ProcessFrame


class ComputerVision:
    """Use computer vision to detect objects."""
    def __init__(self, src=int):
        # Use Webcam... to start a thread for feeding frames to processing.
        self.stream = WebcamVideoStream(src=src).start()
        self.frame = self.stream.read()

    def find_line(self):
        """Detect line, return line position."""
        self.frame = self.stream.read()  # Read frame from camera.
        p_f = ProcessFrame(self.frame)  # Create instance of ProcessFrame
        p_f.prep_image()  # Prepare the frame.
        p_f.get_contour()  # Detect contours in frame.
        return p_f.contour_pos()  # Return contour position in frame.

    def cleanup(self):
        """Release the camera. Perform cleanup."""
        self.cap.release()
