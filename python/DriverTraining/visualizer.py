import cv2
from data_manager import process_data
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import numpy as np

path = "python\DriverTraining\ScanData\BetterData.csv"
# path = "python\DriverTraining\ScanData\HouseScan1.csv"

x_data, y_data = process_data(path, img_size=64)
# x_data = np.expand_dims(x_data, axis=3)

img = None
for i in range(0, x_data.shape[0]):
    im = x_data[i, :, :]

    if img is None:
        img = plt.imshow(x_data[i, :, :], cmap=cm.gray)
    else:
        img.set_data(x_data[i, :, :])
    plt.pause(.05)
    plt.draw()

# cv2.namedWindow("Scan")
# for i in range(0, x_data.shape[0]):
#     img = x_data[i,:,:]
#     cv2.imshow("Scan", )
