import cv2
from computer_vision import ComputerVision


COMP_VIS = ComputerVision(src=1)

while cv2.waitKey(1) != ord('q'):
    cv2.imshow("Frame", COMP_VIS.frame)
    print(COMP_VIS.find_line())

COMP_VIS.cleanup()
