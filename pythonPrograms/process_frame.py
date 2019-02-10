import cv2


class ProcessFrame:
    """Perform various image processing functions."""
    def __init__(self, im):
        self.im = im
        self.show = im
        self.thresh_val = 59
        self.vert_border = 250
        self.h = 0
        self.w = 0
        self.thresh = []
        self.center_x = 0
        self.center_y = 0

    def prep_image(self):
        """Prepare image for contour detection."""
        self.h, self.w, _ = self.im.shape
        gray = cv2.cvtColor(self.im, cv2.COLOR_BGR2GRAY)
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

        if len(contours) > 0:
            # Isolate the largest contour.
            contour = max(contours, key=cv2.contourArea)
            # Get data from largest contour.
            mnt = cv2.moments(contour)
            # Center coordinates of largest contour.
            self.center_x = int(mnt['m10'] / mnt['m00'])
            self.center_y = int(mnt['m01'] / mnt['m00'])
            # Draw contours
            # cv2.drawContours(self.show, contour, -1, (0, 255, 0), 1)
            # Draw "cross hairs" on center of contour.
            # cv2.line(self.show, (self.center_x, 0), (self.center_x, self.h), (0, 0, 255), 2)
            # cv2.line(self.show, (0, self.center_y), (self.w, self.center_y), (0, 0, 255), 2)

    def contour_pos(self):
        """Detect position of contour relative to middle of screen."""
        vert_mid = self.w / 2  # Middle of screen.

        if (vert_mid - 50) <= self.center_x <= (vert_mid + 50):
            return "C"

        # If middle of contour is too far right.
        if self.center_x < (vert_mid - 50):
            return "R"

        # If center of contour is too far left:
        if self.center_x > (vert_mid + 50):
            return "L"

    def position_text(self, direction):
        """Place text on image."""
        # Settings for font, position, color, etc.
        # Assigned to variables to act as labels for each value.
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_pos = (10, 100)
        font_scale = 1
        font_color = (0, 0, 255)
        line_type = 2

        cv2.putText(self.show,
                    direction,
                    text_pos,
                    font,
                    font_scale,
                    font_color,
                    line_type)
