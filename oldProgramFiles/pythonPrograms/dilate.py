from __future__ import print_function
import cv2
import numpy as np
import argparse
morph_size = 0
max_operator = 4
max_elem = 2
max_kernel_size = 21
title_trackbar_operator_type = 'Operator:\n 0: Opening - 1: Closing  \n 2: Gradient - 3: Top Hat \n 4: Black Hat'
title_trackbar_element_type = 'Element:\n 0: Rect - 1: Cross - 2: Ellipse'
title_trackbar_kernel_size = 'Kernel size:\n 2n + 1'
title_window = 'Morphology Transformations Demo'
morph_op_dic = {0: cv2.MORPH_OPEN, 1: cv2.MORPH_CLOSE,
                2: cv2.MORPH_GRADIENT, 3: cv2.MORPH_TOPHAT, 4: cv2.MORPH_BLACKHAT}


def morphology_operations(val):
    threshold = cv2.getTrackbarPos(title_trackbar_operator_type, title_window)
    gray_frame = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    blur_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
    # Adaptive threshold is used to balance shadows and inconsistencies in the frame
    dst = cv2.adaptiveThreshold(blur_frame,
                                threshold,
                                cv2.ADAPTIVE_THRESH_MEAN_C,
                                cv2.THRESH_BINARY_INV,
                                11,
                                2)
    cv2.imshow(title_window, dst)


src = cv2.imread('pythonPrograms/hoseOnDirt.jpg')
new_h = int(src.shape[0] * .1)
new_w = int(src.shape[1] * .1)
dim = (new_w, new_h)
src = cv2.resize(src, dim, interpolation=cv2.INTER_AREA)
cv2.namedWindow(title_window)
cv2.createTrackbar(title_trackbar_operator_type, title_window,
                   0, 255, morphology_operations)
cv2.waitKey()
