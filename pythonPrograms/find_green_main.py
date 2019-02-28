import cv2
import modules.image_processes as im_proc
# from process_frame import ProcessFrame


CAP = cv2.VideoCapture(0)

try:
    while cv2.waitKey(1) != ord('q'):
        _, image = CAP.read()
        im_proc.find_green(image)

except KeyboardInterrupt:
    print("\nProgram closed by user.\n")

cv2.destroyAllWindows()
CAP.release()  # Done with capture
