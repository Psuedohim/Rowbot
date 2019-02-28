import cv2
import modules.image_processes as im_proc
# from process_frame import ProcessFrame


CAP = cv2.VideoCapture(0)

try:
    while cv2.waitKey(1) != ord('q'):
        _, IMAGE = CAP.read()
        threshold = im_proc.threshold_image(IMAGE)
        largest_contour = im_proc.largest_contour(threshold)
        center_x, center_y = im_proc.center_of_contour(largest_contour)
        print(im_proc.contour_location(IMAGE, center_x, center_y))

except KeyboardInterrupt:
    print("\nProgram closed by user.\n")

CAP.release()  # Done with capture.
