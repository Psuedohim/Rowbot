import cv2
import numpy as np


THRESH_VAL = 59
VERT_BORDER = 250


def threshold_image(image):
    """Apply threshold and return image."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # Adaptive threshold is used to balance shadows and
    # inconsistencies in the frame.
    threshold = cv2.adaptiveThreshold(blur,
                                      THRESH_VAL,
                                      cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY_INV,
                                      11,
                                      2)
    # Return thresheld image.
    return threshold


def largest_contour(thresh_image):
    """Detect center of largest contour."""
    # Find all contours in image threshold.
    contours, _ = cv2.findContours(thresh_image,
                                   cv2.RETR_TREE,
                                   cv2.CHAIN_APPROX_NONE)

    if contours:
        # Isolate and return the largest contour.
        return max(contours, key=cv2.contourArea)


def center_of_contour(contour):
    """Return coordinates of center of contour."""
    # Extract data from largest contour.
    mnt = cv2.moments(contour)
    # Get center coordinates of largest contour.
    center_x = int(mnt['m10'] / mnt['m00'])
    center_y = int(mnt['m01'] / mnt['m00'])

    return center_x, center_y


def contour_location(image, center_x, center_y):
    """Detect position of contour relative to middle of screen."""
    # Get size of image. .shape returns y, x.
    image_height, image_width, _ = image.shape
    # Caclulate center of image.
    image_middle = image_width / 2  # Middle of screen.

    # If middle of contour is in-line with middle of screen.
    if (image_middle - 50) <= center_x <= (image_middle + 50):
        return "C"

    # If middle of contour is too far right.
    if center_x < (image_middle - 50):
        return "R"

    # If center of contour is too far left:
    if center_x > (image_middle + 50):
        return "L"


def find_line(image):
    """Find line, return location relative to screen center."""
    threshold = threshold_image(image)
    largest_contour = largest_contour(threshold)
    center_x, center_y = center_of_contour(largest_contour)
    # Print location of line to console for user.
    print(contour_location(image, center_x, center_y))
