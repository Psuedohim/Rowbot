import time
import cv2
# from smbus2 import SMBus
from process_frame import ProcessFrames
# from picamera.array import PiRGBArray
# from picamera import PiCamera

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
# bus = SMBus(1)  # Start bus on /dev/i2c-2.


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
    # try:
    #     bus.write_i2c_block_data(MTR_DRV_ADDR, 0, transfer_data)
    # except OSError:
    #     print("OSError Occurred, Continuing...")
    #     pass


def main():
    # raw_frame = proc.update_frame()  # Capture new frame from camera.
    print('.')
    src = cv2.imread('pythonPrograms/hoseOnChips.jpg')
    print('.')
    new_h = int(src.shape[0] * .2)
    print('.')
    new_w = int(src.shape[1] * .2)
    print('.')
    dim = (new_w, new_h)
    print('.')
    raw_frame = cv2.resize(src, dim, interpolation=cv2.INTER_AREA)
    print('.')

    frame = proc.prep_frame(raw_frame)  # Prepare frame for contour detection.
    # Find largest contour, presumably the hose.
    largest_contour = proc.largest_contour(frame)

    cv2.drawContours(raw_frame, [largest_contour], 0, (0, 0, 255), 3)
    # proc.show_frame(raw_frame)

    # Compute center coordinates of contour.
    center_x, center_y = proc.center_coordinates(largest_contour)
    crosshairs = proc.draw_crosshairs(raw_frame, center_x, center_y)
    proc.show_frame(crosshairs)
    # Return relative position of contour in frame.
    position = proc.contour_pos(center_x, center_y)
    print("Position of Contour: " + position)
    handle_comm('c', 'f')
    # handle_comm(position, 'f')


# def count_loop():
    # LOOP_COUNT += 1
    # print("Loop Count: " + str(LOOP_COUNT))


# camera = PiCamera()
# camera.resolution = (proc.width, proc.height)
# camera.framerate = 32
# rawCapture = PiRGBArray(camera, size=(proc.width, proc.height))

# try:
while True:
    try:
        main()

    except KeyboardInterrupt:
        proc.close()
        handle_comm('x', 'x')
    # for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # raw_image = frame.array
    # main(raw_image)
    # count_loop()
    # rawCapture.truncate(0)
# except:  # Catch any error and close camera.
#     print("Releasing Camera...")
#     proc.close()
#     print("Releasing Motors...")
#     handle_comm('x', 'x')
