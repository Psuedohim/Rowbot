import cv2
import numpy as np


class ProcessColor:

    def __init__(self, image):
        # self.image = cv2.imread(image)
        self.image = image
        self.contour_image = []
        self.low_hue = 31
        self.low_sat = 42
        self.low_val = 149
        self.high_hue = 194
        self.high_sat = 228
        self.high_val = 255

    def green_filter(self):
        blurred = cv2.GaussianBlur(self.image, (13, 13), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        color_low = np.array([self.low_hue,self.low_sat,self.low_val])
        color_high = np.array([self.high_hue, self.high_sat, self.high_val])
        mask = cv2.inRange(hsv, color_low, color_high)
        kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kern)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kern)
        return mask
        # self.contour_image = cv2.threshold(mask, 1, cv2.THRESH_BINARY, 11, 2)
        # return cv2.threshold(mask, 1, cv2.THRESH_BINARY, 11, 2)