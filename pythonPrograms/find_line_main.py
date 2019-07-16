import cv2
import modules.image_processes as im_proc
# from process_frame import ProcessFrame


CAP = cv2.VideoCapture(0)

try:
    while cv2.waitKey(1) != ord('q'):
        _, image = CAP.read()
        im_proc.find_line(image)

except KeyboardInterrupt:
    print("\nProgram closed by user.\n")

CAP.release()  # Done with capture.
