import cv2
import imutils
from imutils.video import WebcamVideoStream
from process_frame import ProcessFrame
from process_color import ProcessColor


class ComputerVision:
    """Use computer vision to detect objects."""
    def __init__(self, src):
        # Use Webcam... to start a thread for feeding frames to processing.
        self.stream = WebcamVideoStream(src=src).start()
        # self.stream = cv2.VideoCapture(src)
        self.frame = self.stream.read()

    def find_line(self):
        """Detect line, return line position."""
        self.frame = self.stream.read()  # Read frame from camera.
        p_f = ProcessFrame(self.frame)  # Create instance of ProcessFrame
        # p_f.start_prep_image()  # Prepare the frame.
        p_f.prep_image()
        p_f.get_contour()  # Detect contours in frame.
        # return p_f.contour_pos()  # Return contour position in frame.
        return p_f.contour_xy_pos()  # Return contour x, y pos.

    def find_weed(self):
        frame = self.stream.read()
        p_c = ProcessColor(frame)
        green_filter = p_c.green_filter()
        # green_filter = p_c.contour_image
        # while cv2.waitKey(0) != ord('q'):
        #     cv2.imshow('im', green_filter)
        # cv2.destroyAllWindows()
        p_f = ProcessFrame(green_filter)
        # x, y = p_f.get_each_contour_pos()
        x = p_f.get_contour_x()
        y = p_f.get_contour_y()
        print("Contour Found. \nx: " + str(x) + "\ny: " + str(y))
        return x, y

    def cleanup(self):
        """Release the camera. Perform cleanup."""
        self.cap.release()
