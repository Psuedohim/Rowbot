import smbus
import time
from modules.process_frame import ProcessFrames

MTR_DRV_ADDR = 1

proc = ProcessFrames(4)  # 4 = USB Camera on Rock Pi.
motor_driver = smbus.SMBus(1)  # Start bus on /ic2-1?

boolToKeepRunning = True

while boolToKeepRunning:
    raw_frame = proc.update_frame()
    frame = proc.prep_frame(raw_frame)
    contours = proc.all_contours(frame)
    biggest_contour = proc.biggest_contour(contours)
    center_x, center_y = proc.center_coordinates(biggest_contour)
    position = proc.contour_pos(center_x, center_x)
    crosshair_frame = proc.draw_crosshairs(raw_frame, center_x, center_y)
    proc.show_frame(crosshair_frame)


def handle_direction(dir_to_go):  # Go forwards.
    if dir_to_go == 'f':
        motor_driver.write_byte(MTR_DRV_ADDR, 4)  # Backwards released.
        motor_driver.write_block(MTR_DRV_ADDR, 1)  # Forwards pressed.

    elif dir_to_go == 'b':  # Go backwards.
        motor_driver.write_byte(MTR_DRV_ADDR, 2)  # Forwards released.
        motor_driver.write_byte(MTR_DRV_ADDR, 3)  # Backwards pressed.

    else:  # Stop, brake.
        motor_driver.write_byte(MTR_DRV_ADDR, 2)  # Forwards released.
        motor_driver.write_byte(MTR_DRV_ADDR, 4)  # Backwards released.


def handle_steering(dir_to_turn):
    if dir_to_turn == 'r':  # Turn right.
        motor_driver.write_byte(MTR_DRV_ADDR, 7)  # Left released.
        motor_driver.write_byte(MTR_DRV_ADDR, 5)  # Right pressed.

    elif dir_to_turn == 'l':  # Turn left.
        motor_driver.write_byte(MTR_DRV_ADDR, 6)  # Right released.
        motor_driver.write_byte(MTR_DRV_ADDR, 7)  # Left pressed.

    else:  # Continue straight.
        motor_driver.write_byte(MTR_DRV_ADDR, 6)  # Right released.
        motor_driver.write_byte(MTR_DRV_ADDR, 7)  # Left released.
