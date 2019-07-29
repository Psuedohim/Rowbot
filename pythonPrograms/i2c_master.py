import smbus
import time
from modules.process_frame import ProcessFrames

MTR_DRV_ADDR = 0x04
FORWARD_FLAG = 0
BACKWARD_FLAG = 1
STOP_FLAG = 2
LEFT_FLAG = 3
RIGHT_FLAG = 4
CENTER_FLAG = 5

proc = ProcessFrames(4)  # 4 = USB Camera on Rock Pi.
motor_driver = smbus.SMBus(2)  # Start bus on /dev/i2c-2.


def handle_direction(dir_to_go):  # Go forwards.
    """Communicate driving direction to slave device over I2C."""
    print(dir_to_go)
    if dir_to_go == 'f':  # Go forwards.
        motor_driver.write_block(MTR_DRV_ADDR, FORWARD_FLAG)

    elif dir_to_go == 'b':  # Go backwards.
        motor_driver.write_byte(MTR_DRV_ADDR, BACKWARD_FLAG)

    else:  # Stop, brake.
        motor_driver.write_byte(MTR_DRV_ADDR, STOP_FLAG)


def handle_steering(dir_to_turn):
    """Communicate steering instruction to slave device over I2C."""
    print(dir_to_turn)
    if dir_to_turn == 'r':  # Turn right.
        motor_driver.write_byte(MTR_DRV_ADDR, 5)

    elif dir_to_turn == 'l':  # Turn left.
        motor_driver.write_byte(MTR_DRV_ADDR, 7)

    else:  # Continue straight.
        motor_driver.write_byte(MTR_DRV_ADDR, 7)


boolToKeepRunning = True

while boolToKeepRunning:
    raw_frame = proc.update_frame()
    frame = proc.prep_frame(raw_frame)
    contours = proc.all_contours(frame)
    biggest_contour = proc.biggest_contour(contours)
    center_x, center_y = proc.center_coordinates(biggest_contour)
    position = proc.contour_pos(center_x, center_x)
    handle_steering(position)
    # crosshair_frame = proc.draw_crosshairs(raw_frame, center_x, center_y)
    # proc.show_frame(crosshair_frame)
