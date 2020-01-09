from smbus2 import SMBus
import time
from modules.process_frame import ProcessFrames

MTR_DRV_ADDR = 0x04
FORWARD_FLAG = 2
BACKWARD_FLAG = 3
STOP_FLAG = 4
LEFT_FLAG = 5
RIGHT_FLAG = 6
CENTER_FLAG = 7
TERMINATE_FLAG = 254
LOOP_COUNT = 0

proc = ProcessFrames(0)  # 4 = USB Camera on Rock Pi.
bus = SMBus(1)  # Start bus on /dev/i2c-2.



def handle_comm(steer_instr, drive_instr):
    """Handle communication of I2C data to RPi."""
    # A dictionary to hold numerical values for each instruction.
    translation_dict = {
        'r': RIGHT_FLAG,
        'l': LEFT_FLAG,
        'c': CENTER_FLAG,
        'f': FORWARD_FLAG,
        'b': BACKWARD_FLAG,
        's': STOP_FLAG,
        'x': TERMINATE_FLAG
    }
    # The data structure to be sent to the arduino. 
    # Holds two values in specific order.
    transfer_data = [translation_dict[steer_instr],
                     translation_dict[drive_instr]
                    ]
    print(transfer_data)
    try:
        bus.write_i2c_block_data(MTR_DRV_ADDR, 0, transfer_data)
    except OSError:
        print("OSError Occurred, Continuing...")
        pass


def main():
    raw_frame = proc.update_frame()  # Capture new frame from camera.
    frame = proc.prep_frame(raw_frame)  # Prepare frame for contour detection.
    contours = proc.all_contours(frame)  # Get list of contours from image.
    biggest_contour = proc.biggest_contour(contours)  # Find largest contour, presumably the hose.
    center_x, center_y = proc.center_coordinates(biggest_contour)  # Compute center coordinates of contour.
    position = proc.contour_pos(center_x, center_x)  # Return relative position of contour in frame.
    print("Position of Contour: " + position)
    handle_comm(position, 'f')

def count_loop():
    LOOP_COUNT += 1
    print("Loop Count: " + str(LOOP_COUNT))

boolToKeepRunning = True

while boolToKeepRunning:
    try:
        main()
        # count_loop()
    except KeyboardInterrupt:
        print("Releasing Camera...")
        proc.close()
        print("Releasing Motors...")
        handle_comm('x', 'x')
