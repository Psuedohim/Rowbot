import numpy as np
from random import randint
import csv
import time
from sklearn.preprocessing import minmax_scale
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from tensorflow.keras.utils import to_categorical


temp_doc = {
    "Scan": 0,
    "Joystick X": 0,
    "Joystick Y": 0,
    "Theta": [],
    "Distance": [],
}
documents = []


def trim_array(thetas, dists, trim_to_size):
    """
    Trims two arrays to a size of `trim_to_size`.
    Trims the same indices from both arrays to maintain paired data.
    Returns two arrays `thetas, dists`.
    """

    if thetas.shape[0] > trim_to_size:  # We need to cut down size of scan.
        drop_list = []
        while len(drop_list) < (thetas.shape[0] - trim_to_size):
            drop = randint(90, 180)  # Only drop measurements from middle.
            if drop not in drop_list:
                drop_list.append(drop)

    thetas = np.delete(thetas, drop_list, axis=0)
    dists = np.delete(dists, drop_list, axis=0)
    # Normalize theta values.
    thetas = minmax_scale(thetas, copy=False)
    # Normalize distance values.
    dists = minmax_scale(dists, copy=False)

    return thetas, dists


def read_into_documents(path):
    """
    Load data from file.
    Return numpy array.
    """
    documents.clear()
    # data = np.genfromtxt(path, delimiter=',')
    # data = pd.read_csv(path, sep=',')
    with open(path, mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            label = row[0]

            if label == "Scan":
                temp_doc[label] = int(row[1])
            elif label == "Joystick X":
                temp_doc[label] = int(row[1])
            elif label == "Joystick Y":
                temp_doc[label] = int(row[1])
            elif label == "Theta":
                temp_doc[label] = []
                for value in row[1:]:
                    temp_doc[label].append(float(value))
            elif label == "Distance":
                temp_doc[label] = []
                for value in row[1:]:
                    temp_doc[label].append(int(value))

                documents.append({
                    "Scan": temp_doc["Scan"],
                    "Joystick X": temp_doc["Joystick X"],
                    "Joystick Y": temp_doc["Joystick Y"],
                    "Theta": temp_doc["Theta"],
                    "Distance": temp_doc["Distance"]
                })
    print(F"Filled {len(documents)} documents.\n")

    # return documents


def log_scale_list(array_to_scale, max_val):
    """
        Perform min/max scaling on entire vector.
        Parameters:
                array_to_scale - Numpy array containing unscaled float values.
                max_val - Maximum value for scale.
    """
    array_to_scale = np.divide(
        # np.log1p(np.log1p(array_to_scale)), np.log(np.log(17000))
        # np.log1p(array_to_scale), np.log(17000)
        np.sqrt(np.sqrt(array_to_scale)), np.sqrt(np.sqrt(17000))
    )
    scaled_array = np.multiply(array_to_scale, max_val)
    return scaled_array


def process_data(path, img_size=32):
    """
    Load data from file.
    Return numpy array of processed data in form [[(theta, distance), steer_angle], ...]
    """
    # documents = []
    read_into_documents(path)
    num_docs = len(documents)
    # img_size = 32
    # num_meas = 250  # Number of measurements to keep for training.
    img_center = int(img_size / 2)
    # Initialize output array.
    x_data = np.zeros((num_docs, img_size, img_size))
    y_data = np.zeros((num_docs, 2))

    for i in range(0, num_docs):
        doc = documents[i]
        # Insert joystick positions to y_data.
        y_data[i, 0] = doc["Joystick X"]
        y_data[i, 1] = doc["Joystick Y"]

        # Generate numpy arrays from scan data.
        thetas = np.array(doc["Theta"])
        dists = np.array(doc["Distance"])
        dists = log_scale_list(dists, img_center - 1)
        # thetas, dists = trim_array(thetas, dists, trim_to_size=250)  # Trim size of scan.
        # Calculate "true" x-y-coordinates for plotting scan.
        x_coords = dists * np.sin(np.radians(thetas))
        y_coords = dists * np.cos(np.radians(thetas))
        # Convert coordinates to integer for indexing.
        x_coords = x_coords.astype(int)
        y_coords = y_coords.astype(int)
        # Account for origin of scan at center of image, not TL corner.
        x_coords += img_center
        y_coords = -y_coords + img_center
        # Insert scan data to output array.
        x_data[i, y_coords, x_coords] = 1

    # Normalize joystick positions to range [-1, 1].
    y_data[:, :] /= 127
    x_data = np.expand_dims(x_data, axis=3)

    return x_data, y_data


def gen_lstm_inputs(x_data, y_data, t_steps, skip_steps):
    print(F"Init X_Data: {x_data.shape}")
    while x_data.shape[0] % t_steps > 0:
        x_data = np.delete(x_data, -1, axis=0)

    print(F"trim X_Data: {x_data.shape}")
    n_batches = int(x_data.shape[0] / t_steps)
    lstm_inputs = np.zeros(
        (n_batches, t_steps, x_data.shape[1], x_data.shape[2], x_data.shape[3]))

    lstm_outputs = np.zeros((n_batches, 2))

    for i in range(0, n_batches - skip_steps, skip_steps):
        for j in range(0, t_steps):
            lstm_inputs[i, j, :, :, :] = x_data[i + j, :, :, :]
            lstm_outputs[i, :] = y_data[i + j, :]

    return lstm_inputs, lstm_outputs


def gen_categorical(y_data, num_classes):
    y_data += 1  # Normalize values to [0, 2] for categorizing.
    y_data *= (num_classes/2)
    return to_categorical(y_data, num_classes=num_classes + 1)


def test_train_split(x_data, y_data, test_size=1500):
    x_train = x_data[:-test_size, :, :]
    x_test = x_data[-test_size:, :, :]
    y_train = y_data[:-test_size, :]
    y_test = y_data[-test_size:, :]

    y_train = y_train.astype("float32")
    y_test = y_test.astype("float32")

    return x_test, x_train, y_test, y_train


if __name__ == "__main__":
    # path_to_data = "python/DriverTraining/ScanData/BetterData.csv"
    path_to_data = "python/DriverTraining/ScanData/HouseScan1.csv"
    start_time = time.time()
    print("Test for `data_manager.py`\n")

    """Begin testing for Data Manager."""
    x_data, y_data = process_data(path_to_data)

    img = x_data[-1, :, :]
    print(F"Shape of img: {img.shape}\n")
    plt.imshow(img, cmap=cm.gray)
    plt.show()

    print(F"Shape of returned x_data: {x_data.shape}\n")
    print(F"Shape of returned y_data: {y_data.shape}\n")
    # print(F"First of x_data: {x_data[0, :]}\n")
    print(F"First 10 of y_data: {y_data[0:10]}\n")
    """End testing for Data Manager."""

    max_dists = []
    read_into_documents(path_to_data)

    for doc in documents:
        max_dists.append(max(doc["Distance"]))

    print(F"Max Distance from all scans: {max(max_dists)}\n")

    end_time = time.time()
    print(F"Time to complete: {end_time - start_time}\n")
