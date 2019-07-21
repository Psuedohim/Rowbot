import smbus
import time
from modules.process_frame_v2 import ProcessFrames 


proc = ProcessFrames(0)
# bus = smbus.SMBus(1)
motor_addr = 1

boolToKeepRunning = True

while boolToKeepRunning:
    raw_frame = proc.update_frame()
    frame = proc.prep_frame(raw_frame)
    contours = proc.all_contours(frame)
    biggest_contour = proc.biggest_contour(contours)
    center_x, center_y = proc.center_coordinates(biggest_contour)
    position = proc.contour_pos(center_x, center_x)
    
    