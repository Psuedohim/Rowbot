import cv2


def nothing():
    """Mock function for trackbar."""
    # pass

PATH = "images/weed_demo.mov"

CAP = cv2.VideoCapture(PATH)

cv2.namedWindow('Binary Threshold')
cv2.createTrackbar('Threshold Value', 'Binary Threshold', 0, 255, nothing)
KEY_PRESS = 0
while KEY_PRESS != 27:
    _, IMAGE = CAP.read()
    IMAGE = cv2.cvtColor(IMAGE, cv2.COLOR_BGR2GRAY)
    KEY_PRESS = cv2.waitKey(1)
    BINARY_THRESH_VAL = cv2.getTrackbarPos('Threshold Value', 'Binary Threshold')
    _, BINARY_THRESH_IMG = cv2.threshold(IMAGE,
                                         BINARY_THRESH_VAL,
                                         255,
                                         cv2.THRESH_BINARY_INV)
    cv2.imshow('Binary Threshold', BINARY_THRESH_IMG)
