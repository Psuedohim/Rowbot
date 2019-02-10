import cv2
from pythonPrograms.process_frame import ProcessFrame


class ComputerVision:
    """Use computer vision to detect objects."""
    def __init__(self, camera=int):
        self.cap = cv2.VideoCapture(camera)

    def find_line(self):
        """Detect line, return line position."""
        _, frame = self.cap.read()  # Read frame from camera.
        pf = ProcessFrame(frame)  # Create instance of ProcessFrame
        pf.prep_image()  # Prepare the frame.
        pf.get_contour()  # Detect contours in frame.
        return pf.contour_pos()  # Return contour position in frame.

    def cleanup(self):
        """Release the camera. Perform cleanup."""
        self.cap.release()
