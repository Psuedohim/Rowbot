import cv2
from threading import Thread


class ProcessFrames:
    """Perform various image processing functions."""

    def __init__(self, camera):  # Pass address to camera (0 = builtin).
        self.capture = cv2.VideoCapture(camera)
        self.thresh_val = 59  # Threshold value
        self.height = 0
        self.width = 0
        self.dev = 50  # Deviance allowed for contour to be within center.
        self.invalid_frame = False  # In case of invalid frame.

    def update_frame(self):
        """Returns the most recent frame from the camera."""
        if self.capture.isOpened():
            _, frame = self.capture.read()  # Get most recent frame.
            # For use in other functions.
            self.height, self.width, _ = frame.shape
            return frame

        else:
            print("Camera not available.\nExiting Program.")
            exit()

    def prep_frame(self, frame_to_prep):
        """Return an frame that is prepared for contour detection."""
        gray_frame = cv2.cvtColor(frame_to_prep, cv2.COLOR_BGR2GRAY)
        blur_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
        # Adaptive threshold is used to balance shadows and
        # inconsistencies in the frame
        frame = cv2.adaptiveThreshold(blur_frame,
                                      self.thresh_val,
                                      cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY_INV,
                                      11,
                                      2)

        return frame

    def all_contours(self, frame_to_search):
        """Find all contours in a frame. Return sorted list."""
        contours, _ = cv2.findContours(frame_to_search,
                                       cv2.RETR_TREE,
                                       cv2.CHAIN_APPROX_NONE)

        # Return sorted list, biggest -> smallest, if list not empty.
        if contours:
            return sorted(contours, key=cv2.contourArea, reverse=True)
        else:
            # Return empty list.
            return []

    def biggest_contour(self, list_of_contours):
        """Return x, y coordinates to center of the largest contour in a list."""
        # Isolate and return largest contour from list.
        try:
            return max(list_of_contours, key=cv2.contourArea)
        except ValueError:
            print("Value error: Contour considered null.")
            return -1

    def center_coordinates(self, contour):
        """Returns coordinates, x, y, of contour."""
        try: 
            if contour == -1:  # If contour is null,
                print("Contour is null.")
                return -1, -1  # Return null coordinates.
        except ValueError:  # Error from ambiguiously comparing contour obj with
                            # numerical value.
            # print("Contour not null.")
            pass

        # Else, contour is not null. Continue to processing.
        try:  # Try to calculate center of contour.
            mnt = cv2.moments(contour)  # Get data from largest contour.
            center_x = int(mnt['m10'] / mnt['m00'])
            center_y = int(mnt['m01'] / mnt['m00'])
            return center_x, center_y
        # except ZeroDivisionError:
        except:
            # If calculating center fails, send null coordinates.
            # print("Division By Zero Error, Continuing...")
            print("Some error occurred")
            return -1, -1

    def draw_crosshairs(self, frame, x, y):
        """Return frame with crosshair drawn at x, y coordinates."""
        color = (0, 0, 255)
        thickness = 3
        # Draw horizontal line on frame.
        cv2.line(frame, (0, y), (self.width, y), color, thickness)
        # Draw vertical line on frame.
        cv2.line(frame, (x, 0), (x, self.height), color, thickness)
        return frame

    def show_frame(self, frame_to_show):
        cv2.imshow("Current Frame", frame_to_show)
        # cv2.waitKey(0)  # Wait for key press to continue.

    def contour_pos(self, center_x, center_y):
        """Detect position of contour relative to center of frame."""
        vert_mid = self.width / 2  # Middle of frame, vertically.
        # If center of contour is to the left side of the frame.
        if center_x < 0 and center_y < 0:  # If coordinates were considered null,
            return 'c'  # Continue straight.
        elif center_x < (vert_mid - self.dev):
            return 'l'
        # If center of contour is to the right side of frame,
        elif center_x > (vert_mid + self.dev):
            return 'r'  # Go right.
        # If center of contour is within the center of frame.
        else:
            return 'c'
    
    def close(self):
        self.capture.release()
        return
