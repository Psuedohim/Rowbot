import cv2


def nothing(x):
    pass


cap = cv2.VideoCapture(0)
cv2.namedWindow('Binary Threshold')
cv2.createTrackbar('Threshold Value', 'Binary Threshold', 0, 255, nothing)
k1 = 0
while k1 != 27:
    _, im = cap.read()
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    k1 = cv2.waitKey(1)
    binary_thresh_val = cv2.getTrackbarPos('Threshold Value', 'Binary Threshold')
    _, binary_thresh_img = cv2.threshold(im,
                                         binary_thresh_val,
                                         255,
                                         cv2.THRESH_BINARY_INV)
    cv2.imshow('Binary Threshold', binary_thresh_img)
