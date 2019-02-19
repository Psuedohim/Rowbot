import cv2
from process_frame import ProcessFrame


CAP = cv2.VideoCapture(1)

while cv2.waitKey(1) != ord('q'):
    _, IMAGE = CAP.read()
    PF = ProcessFrame(IMAGE)
    PF.prep_IMAGEage()
    PF.get_contour()
    PF.contour_pos()
    # Create window, set to fullscreen.
    cv2.namedWindow("Frame", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Frame", PF.show)

CAP.release()  # Done with capture.
cv2.destroyAllWindows()
