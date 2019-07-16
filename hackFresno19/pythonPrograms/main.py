import cv2
import serial
import time
from computer_vision import ComputerVision


SER = serial.Serial("/dev/cu.usbmodem14301",9600)
# COMP_VIS = ComputerVision(src='images/weed_demo.mov')
# COMP_VIS = ComputerVision('images/weed_demo.mov')
COMP_VIS = ComputerVision(0)

while cv2.waitKey(1) != ord('q'):
    # time.sleep(0.25)
    cv2.imshow("Frame", COMP_VIS.frame)
    # print(COMP_VIS.find_line())
    # SER.write(COMP_VIS.find_line().encode())
    SER.write(str(COMP_VIS.find_weed()).encode())
    # time.sleep(.01)


COMP_VIS.cleanup()
