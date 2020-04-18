import cv2
import argparse


def nothing(x):
    pass


def binary_thresh(image):
    cv2.namedWindow('Binary Threshold')
    cv2.createTrackbar('Threshold Value', 'Binary Threshold', 0, 255, nothing)
    k1 = 0
    while k1 != 27:
        k1 = cv2.waitKey(1)
        binary_thresh_val = cv2.getTrackbarPos('Threshold Value', 'Binary Threshold')
        _, binary_thresh_img = cv2.threshold(image,
                                             binary_thresh_val,
                                             255,
                                             cv2.THRESH_BINARY)
        cv2.imshow('Binary Threshold', binary_thresh_img)


def gaussian_thresh(image):
    cv2.namedWindow('Gaussian Threshold')
    cv2.createTrackbar('threshold', 'Gaussian Threshold', 0, 255, nothing)
    cv2.createTrackbar('Save', 'Binary Threshold', 0, 1, nothing)
    k2 = 0
    while k2 != 27:
        k2 = cv2.waitKey(1)
        gaussian_thresh_val = cv2.getTrackbarPos('threshold', 'Gaussian Threshold')
        gaussian_thresh_img = cv2.adaptiveThreshold(image,
                                                    255,
                                                    # block_size,
                                                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                    cv2.THRESH_BINARY_INV,
                                                    11,
                                                    gaussian_thresh_val)
        cv2.imshow('Gaussian Threshold', gaussian_thresh_img)


def mean_thresh(image):
    cv2.namedWindow('Mean Threshold')
    cv2.createTrackbar('threshold', 'Mean Threshold', 0, 20, nothing)
    k3 = 0
    while k3 != 27:
        k3 = cv2.waitKey(1)
        mean_thresh_val = cv2.getTrackbarPos('threshold', 'Mean Threshold')
        mean_thresh = cv2.adaptiveThreshold(image,
                                            255,
                                            cv2.ADAPTIVE_THRESH_MEAN_C,
                                            cv2.THRESH_BINARY,
                                            9,
                                            mean_thresh_val)
        cv2.imshow('Mean Threshold', mean_thresh)


def to_zero_thresh(image):
    cv2.namedWindow('To Zero Threshold')
    cv2.createTrackbar('threshold', 'To Zero Threshold', 0, 255, nothing)
    k4 = 0
    while k4 != 27:
        k4 = cv2.waitKey(1)
        to_zero_thresh_val = cv2.getTrackbarPos('threshold', 'To Zero Threshold')
        _, to_zero_thresh_img = cv2.threshold(image, to_zero_thresh_val, 255, cv2.THRESH_TOZERO)
        cv2.imshow('To Zero Threshold', to_zero_thresh_img)
        if k4 == 129:
            cv2.imwrite('images/cropped_images/thresh_img.png', image)
        else:
            continue


def canny(image):
    img = image
    blur = cv2.bilateralFilter(img, 11, 17, 17)
    while True:
        canny_min = 0
        canny_max = 1
        edged = cv2.Canny(blur, canny_min, canny_max)
        # Find contours in image, keep largest.
        _, contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
        cv2.namedWindow('canny')
        cv2.createTrackbar('canny_min', 'canny', 0, 5000, nothing)
        cv2.createTrackbar('canny_max', 'canny', 0, 5000, nothing)

        # while True:
        canny_min = cv2.getTrackbarPos('canny_min', 'canny')
        canny_max = cv2.getTrackbarPos('canny_max', 'canny')
        for contour in contours:
            # Approximate contour
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.000001 * perimeter, True)
            # Bounding rect.
            x, y, w, h = cv2.boundingRect(contour)

            if w > 100 and h > 100:
                cropped_img = img[y:y + h, x:x + w]
                # Threshold the now cropped image
                _, thresh_cropped_img = cv2.threshold(cropped_img,
                                                      40,
                                                      255,
                                                      cv2.THRESH_BINARY)

            cv2.drawContours(img, [approx], -1, (0, 255, 0), 3)
            cv2.imshow('canny', img)


def cli_menu(image):
    running = True
    while running:
        error = "Invalid input"
        choice = input("""
        \n\t\tThis application is designed to help you choose a threshold
        value for image processing. Choose your desired threshold process(Default = 1).
        To exit image view at any time, press esc.
        \n\t\t1: Binary Threshold\n\t\t2: Gaussian Threshold\n\t\t3: Mean Threshold
        4: Threshold To Zero\n\t\t5: Canny
        \n\t\t9: Quit\n\n\t\t> """)
        if choice == '1':
            binary_thresh(image)
        elif choice == '2':
            gaussian_thresh(image)
        elif choice == '3':
            mean_thresh(image)
        elif choice == '4':
            to_zero_thresh(image)
        elif choice == '5':
            canny(image)
        elif choice == '9':
            print("Exiting Program")
            running = False
        else:
            print(error)


image = cv2.imread("images/to_tune.JPG")

cli_menu(image)