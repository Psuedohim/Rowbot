import cv2
from pythonPrograms.process_frame import ProcessFrame


class ComputerVision:
    """Use computer vision to detect objects."""
    def __init__(self, camera=int):
        self.cap = cv2.VideoCapture(camera)

    def find_line(self):
        """Detect line, return line position."""
        _, frame = self.cap.read()  # Read frame from camera.
        p_f = ProcessFrame(frame)  # Create instance of ProcessFrame
        p_f.prep_image()  # Prepare the frame.
        p_f.get_contour()  # Detect contours in frame.
        return p_f.contour_pos()  # Return contour position in frame.

    def cleanup(self):
        """Release the camera. Perform cleanup."""
        self.cap.release()
