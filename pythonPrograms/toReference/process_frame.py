import cv2
from threading import Thread


class ProcessFrame:
    """Perform various image processing functions."""

    def __init__(self, image):
        self.image = image
        self.thresh_val = 59
        self.vert_border = 250
        self.height = 0
        self.width = 0
        self.thresh = []
        self.center_x = 0
        self.center_y = 0

    def start_prep_image(self):
        """Create a thread for image processing."""
        prep_thread = Thread(target=self.prep_image,
                             name="Prepare Image",
                             args=(),
                             daemon=True)

        prep_thread.start()
        return self

    def prep_image(self):
        """Prepare image for contour detection."""
        self.height, self.width, _ = self.image.shape
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # Adaptive threshold is used to balance shadows and
        # inconsistencies in the frame.
        self.thresh = cv2.adaptiveThreshold(blur,
                                            self.thresh_val,
                                            cv2.ADAPTIVE_THRESH_MEAN_C,
                                            cv2.THRESH_BINARY_INV,
                                            11,
                                            2)

    def get_contour(self):
        """Detect and position cross hairs on center of largest contour."""
        # Find Contours.
        contours, _ = cv2.findContours(self.thresh.copy(),
                                       cv2.RETR_TREE,
                                       cv2.CHAIN_APPROX_NONE)

        if contours:
            # Isolate the largest contour.
            contour = max(contours, key=cv2.contourArea)
            # Get data from largest contour.
            mnt = cv2.moments(contour)
            # Center coordinates of largest contour.
            try:  # Try to calculate center of contour.
                self.center_x = int(mnt['m10'] / mnt['m00'])
                self.center_y = int(mnt['m01'] / mnt['m00'])
            except ZeroDivisionError:  # Catch division by zero.
                pass  # Continue on if division by zero occurs.

    def contour_pos(self):
        """Detect position of contour relative to middle of screen."""
        vert_mid = self.width / 2  # Middle of screen.

        if (vert_mid - 50) <= self.center_x <= (vert_mid + 50):
            return "C"

        # If middle of contour is too far right.
        if self.center_x < (vert_mid - 50):
            return "R"

        # If center of contour is too far left:
        if self.center_x > (vert_mid + 50):
            return "L"
