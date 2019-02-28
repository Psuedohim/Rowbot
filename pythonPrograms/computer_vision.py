import cv2
import pythonPrograms.image_processes as im_proc


def find_line(image):
    """Find line, return location."""
    threshold = im_proc.threshold_image(image)
    largest_contour = im_proc.largest_contour(threshold)
    center_x, center_y = im_proc.center_of_contour(largest_contour)
    print(im_proc.contour_location(image, center_x, center_y))

# class ComputerVision:
#     def __init__(self, camera=int):
#         self.cap = cv2.VideoCapture(camera)

#     def find_line(self):


#     def cleanup(self):
#         self.cap.release()
