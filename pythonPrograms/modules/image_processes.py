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


def all_contours(thresh_image):
    """Find all contours in an image. Return sorted list."""
    # Find all contours in image threshold.
    contours, _ = cv2.findContours(thresh_image,
                                   cv2.RETR_TREE,
                                   cv2.CHAIN_APPROX_NONE)

    if contours:
        return sorted(contours, key=cv2.contourArea, reverse=True)


def coordinates_of_contour(contour):
    """Return coordinates of center of contour."""
    # Extract data from largest contour.
    mnt = cv2.moments(contour)
    # Get center coordinates of largest contour.
    try:  # Caclulations may result in x/0, causing an error.
        center_x = int(mnt['m10'] / mnt['m00'])
        center_y = int(mnt['m01'] / mnt['m00'])
        return center_x, center_y
    except ZeroDivisionError:
        pass  # Continue program when division by zero occurs.


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


def filter_green(image):
    """Filter all green that is within range, from the image."""
    # Values obtained using programs from tools/, tuned to specific image.
    low_hue = 31
    low_saturation = 42
    low_value = 149
    high_hue = 194
    high_saturation = 228
    high_value = 255

    blur = cv2.GaussianBlur(image, (13, 13), 0)
    hsv_image = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    filter_low = np.array([low_hue, low_saturation, low_value])
    filter_high = np.array([high_hue, high_saturation, high_value])
    # Get mask using low and high filtering values.
    mask_image = cv2.inRange(hsv_image, filter_low, filter_high)

    return mask_image


def clean_filtered_image(mask_image):
    """Remove noise from binary image."""
    # Create ellipse around objects.
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    # Filter noise outside of filter.
    mask = cv2.morphologyEx(mask_image, cv2.MORPH_OPEN, kernel)
    # Filter noise inside of filter.
    mask = cv2.morphologyEx(mask_image, cv2.MORPH_CLOSE, kernel)

    return mask


def find_line(image):
    """Find line, return location relative to screen center."""
    threshold = threshold_image(image)
    try:  # May result in error if no contours are detected.
        largest_contour = all_contours(threshold)[0]
        center_x, center_y = coordinates_of_contour(largest_contour)
        # Print location of line to console for user.
        print(contour_location(image, center_x, center_y))
    except TypeError:
        print("\nNo lines found.")
        pass


def find_green(image):
    # Filter green in image.
    filtered = filter_green(image)
    try:  
        # May result in TypeError if no contours are found.
        contours = all_contours(filtered)
        for contour in contours:
            center_x, center_y = coordinates_of_contour(contour)
            print(center_x, center_y)
    except TypeError:
        print("\nNo contours found.")

