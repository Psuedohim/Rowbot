import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers
import time
import matplotlib.pyplot as plt

from data_manager import process_data, test_train_split, gen_lstm_inputs, gen_categorical, augment_append_data

# Create a base template for A/B testing of model parameters.
BASE_PARAMS = {
    "scan_shape": (64, 64, 1),
    "img_shape": (80, 128, 1),
    "activation": "relu",
    "padding": "same",
    "regularizer": regularizers.l1(0.0001),
    "conv1n": 8,
    "conv2n": 32,
    "conv3n": 32,
    "conv4n": 32,
    "conv1f": 3,
    "conv2f": 3,
    "conv3f": 3,
    "conv4f": 3,
    "conv1s": 1,
    "conv2s": 1,
    "conv3s": 1,
    "conv4s": 1,
    "pool1s": 2,
    "pool2s": 2,
    "pool3s": 2,
    "dense1n": 64,
    "dense2n": 64,
    "dense3n": 64,
    "dense4n": 32,
    "dense5n": 32,
    "dense6n": 32,
    "dropout": 0.5,
    "output_activation": "tanh",
}


def get_compiled_cnn(params):
    """ Build a Keras Convolutional Neural Network using specified model parameters.

    Parameters
    ----------
        params: Extension of BASE_PARAMS.
            Parameters used in creation of a new model.

    Returns
    -------
        model: Keras Convolutional Neural Network Model.
    """

    activation = params["activation"]
    padding = params["padding"]
    reg = params["regularizer"]
    # Create input for rangescan data.
    scan_input = keras.Input(shape=params["scan_shape"], name="scan_input")
    # Create input for monocular image data.
    img_input = keras.Input(shape=params["img_shape"], name="image_input")

    # Process Scan input.
    x_scan = layers.Conv2D(params["conv1n"],
                           params["conv1f"],
                           strides=params["conv1s"],
                           padding=padding,
                           activation=activation,
                           name="conv1")(scan_input)
    x_scan = layers.MaxPooling2D(
        pool_size=params["pool1s"], name="pool1")(x_scan)
    x_scan = layers.Flatten()(x_scan)

    # Process Image input.
    x_img = layers.Conv2D(params["conv2n"],
                          params["conv2f"],
                          strides=params["conv2s"],
                          padding=padding,
                          activation=activation,
                          name="conv2")(img_input)
    x_img = layers.AveragePooling2D(
        pool_size=params["pool2s"], name="pool2")(x_img)
    x_img = layers.Conv2D(params["conv3n"],
                          params["conv3f"],
                          strides=params["conv3s"],
                          padding=padding,
                          activation=activation,
                          name="conv3")(img_input)
    x_img = layers.AveragePooling2D(pool_size=3)(x_img)
    x_img = layers.Conv2D(params["conv4n"],
                          params["conv4f"],
                          strides=params["conv4s"],
                          padding=padding,
                          activation=activation,
                          activity_regularizer=reg,
                          name="conv4")(x_img)
    x_img = layers.AveragePooling2D(
        pool_size=params["pool3s"], name="pool3")(x_img)
    x_img = layers.Flatten()(x_img)

    # Concatenate inputs to singular tensor before processing continues.
    x = layers.Concatenate(axis=1)([x_scan, x_img])

    # Pass tensor to fully connected portion of network.
    x = layers.Dense(params["dense1n"], activation=activation,
                     name="dense_1", activity_regularizer=reg)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(params["dense2n"], activation=activation,
                     name="dense_2", activity_regularizer=reg)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(params["dense3n"], activation=activation,
                     name="dense_3", activity_regularizer=reg)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(params["dense4n"], activation=activation,
                     name="dense_4", activity_regularizer=reg)(x)
    x = layers.Dropout(params["dropout"])(x)
    x = layers.Dense(params["dense5n"], activation=activation,
                     name="dense_5", activity_regularizer=reg)(x)
    x = layers.Dropout(params["dropout"])(x)
    x = layers.Dense(params["dense6n"], activation=activation,
                     name="dense_6", activity_regularizer=reg)(x)
    x = layers.Dropout(params["dropout"])(x)

    # Define output layer with two nodes for virtual-x-y positions.
    output_x = layers.Dense(2, activation=params["output_activation"],
                            name="x_y_out")(x)  # Tanh: [-1, 1]

    # Define the Keras model input and output nodes.
    model = keras.Model(inputs=[scan_input, img_input], outputs=output_x)
    # Compile Keras model with Adam, MSE loss, and MAE metric.
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.0001),  # Optimizer
        loss=tf.keras.losses.MeanSquaredError(),
        metrics=[tf.keras.metrics.MeanAbsoluteError()],
    )

    return model


if __name__ == "__main__":
    # Keep track of program run time.
    start_time = time.time()

    # Define image sizes and training parameters.
    img_size = 64
    batch_size = 128
    num_epochs = 100

    # Define system paths to training data files.
    path_to_train = "python\DriverTraining\ScanData\ImgScanData_training.csv"
    path_to_train_no_img = "python\DriverTraining\ScanData\OldScans\TrainingData.csv"
    path_to_test = "python\DriverTraining\ScanData\CSUArtScan.csv"
    path_to_test_no_img = "python\DriverTraining\ScanData\OldScans\TestData.csv"

    # Process data from file to NumPy arrays.
    x_scan_train, x_img_train, y_train = process_data(
        path_to_train, scan_img_size=img_size)
    x_scan_test, x_img_test, y_test = process_data(
        path_to_test, scan_img_size=img_size)
    x_scan_train_gen, x_img_train_gen, y_train_gen = process_data(
        path_to_train_no_img, scan_img_size=img_size, no_img=True)

    x_scan_train = np.append(x_scan_train, x_scan_train_gen, axis=0)
    x_img_train = np.append(x_img_train, x_img_train_gen, axis=0)
    y_train = np.append(y_train, y_train_gen, axis=0)

    x_scan_train, x_img_train, y_train = augment_append_data(
        x_scan_train, x_img_train, y_train)
    x_scan_test, x_img_test, y_test = augment_append_data(
        x_scan_test, x_img_test, y_test)

    scan_val, img_val, y_val, scan_train, img_train, y_train = test_train_split(
        x_scan_train, x_img_train, y_train)

    param_test_list = []

    param_test_0 = BASE_PARAMS.copy()
    param_test_0["activation"] = "relu"
    param_test_0["conv1n"] = 32  # Conv on scan image.
    param_test_0["conv2n"] = 64
    param_test_0["conv3n"] = 64
    param_test_0["conv4n"] = 128
    param_test_0["conv1f"] = 1
    param_test_0["conv2f"] = 1
    param_test_0["conv3f"] = 1
    param_test_0["conv4f"] = 1
    param_test_0["pool1s"] = 6
    param_test_0["pool2s"] = 6
    param_test_0["pool3s"] = 6
    param_test_0["dense1n"] = 1028
    param_test_0["dense2n"] = 1028
    param_test_0["dense3n"] = 512
    param_test_0["dense4n"] = 512
    param_test_0["dropout"] = 0.5
    param_test_list.append(param_test_0)

    param_test_1 = BASE_PARAMS.copy()
    param_test_1["activation"] = "relu"
    param_test_1["regularizer"] = None
    param_test_1["conv1n"] = 32  # Conv on scan image.
    param_test_1["conv2n"] = 64
    param_test_1["conv3n"] = 64
    param_test_1["conv4n"] = 128
    param_test_1["conv1f"] = 1
    param_test_1["conv2f"] = 1
    param_test_1["conv3f"] = 1
    param_test_1["conv4f"] = 1
    param_test_1["pool1s"] = 6
    param_test_1["pool2s"] = 6
    param_test_1["pool3s"] = 6
    param_test_1["dense1n"] = 1028
    param_test_1["dense2n"] = 1028
    param_test_1["dense3n"] = 512
    param_test_1["dense4n"] = 512
    param_test_1["dropout"] = 0.5
    param_test_list.append(param_test_1)

    param_test_2 = BASE_PARAMS.copy()
    param_test_2["activation"] = "relu"
    param_test_2["conv1n"] = 32  # Conv on scan image.
    param_test_2["conv2n"] = 64
    param_test_2["conv3n"] = 64
    param_test_2["conv4n"] = 128
    param_test_2["conv1f"] = 1
    param_test_2["conv2f"] = 1
    param_test_2["conv3f"] = 1
    param_test_2["conv4f"] = 1
    param_test_2["pool1s"] = 6
    param_test_2["pool2s"] = 6
    param_test_2["pool3s"] = 6
    param_test_2["dense1n"] = 1028
    param_test_2["dense2n"] = 1028
    param_test_2["dense3n"] = 512
    param_test_2["dense4n"] = 512
    param_test_2["dropout"] = 0.1
    param_test_list.append(param_test_2)

    param_test_3 = BASE_PARAMS.copy()
    param_test_3["activation"] = "relu"
    param_test_3["regularizer"] = None
    param_test_3["conv1n"] = 32  # Conv on scan image.
    param_test_3["conv2n"] = 64
    param_test_3["conv3n"] = 64
    param_test_3["conv4n"] = 128
    param_test_3["conv1f"] = 1
    param_test_3["conv2f"] = 1
    param_test_3["conv3f"] = 1
    param_test_3["conv4f"] = 1
    param_test_3["pool1s"] = 6
    param_test_3["pool2s"] = 6
    param_test_3["pool3s"] = 6
    param_test_3["dense1n"] = 1028
    param_test_3["dense2n"] = 1028
    param_test_3["dense3n"] = 512
    param_test_3["dense4n"] = 512
    param_test_3["dropout"] = 0.1
    param_test_list.append(param_test_3)

    param_test_4 = BASE_PARAMS.copy()
    param_test_4["activation"] = "relu"
    param_test_4["regularizer"] = None
    param_test_4["conv1n"] = 32  # Conv on scan image.
    param_test_4["conv2n"] = 64
    param_test_4["conv3n"] = 128
    param_test_4["conv4n"] = 256
    param_test_4["conv1f"] = 1
    param_test_4["conv2f"] = 1
    param_test_4["conv3f"] = 1
    param_test_4["conv4f"] = 1
    param_test_4["pool1s"] = 6
    param_test_4["pool2s"] = 6
    param_test_4["pool3s"] = 6
    param_test_4["dense1n"] = 1028
    param_test_4["dense2n"] = 1028
    param_test_4["dropout"] = 0.5
    param_test_list.append(param_test_2)

    for i in range(0, len(param_test_list)):
        print(F"*\n*\n*\n\tTesting Model no. {i}\n*\n*\n*")
        parameters = param_test_list[i]
        model = get_compiled_cnn(parameters)
        keras.utils.plot_model(model, to_file=F"models\modelArch{i}.png")
        model.summary()
        my_callbacks = [keras.callbacks.EarlyStopping(patience=3)]

        print("Fit model on training data")
        history = model.fit(
            [scan_train, img_train],
            y_train,
            batch_size=batch_size,
            epochs=num_epochs,
            validation_data=([scan_val, img_val], y_val),
            callbacks=my_callbacks,
            verbose=1,
        )

        model.save(F"models/trained_model_{i}.h5")

        results = model.evaluate(
            [x_scan_test, x_img_test], y_test, batch_size=batch_size)

        # Plot MAE Lines.
        plt.plot([0, len(history.history['loss'])],
                 [results[1], results[1]],
                 color='r', label="Test MAE")
        plt.plot(history.history['val_mean_absolute_error'],
                 color='b', label="Validation MAE")
        plt.plot(history.history['mean_absolute_error'],
                 color='g', label="Training MAE")
        plt.title(F'Mean Absolute Error for Model {i}')
        plt.ylabel('Mean Absolute Error')
        plt.xlabel('Epoch')

        plt.legend()
        plt.show()
        plt.savefig(F"models\MAEModelPlot{i}.png")
        plt.clf()

        # Plot MSE Lines.
        plt.plot([0, len(history.history['loss'])],
                 [results[0], results[0]],
                 color='r', label="Test MSE")
        plt.plot(history.history['val_loss'],
                 color='b', label="Validation MSE")
        plt.plot(history.history['loss'], color='g', label="Training MSE")
        plt.title(F'Mean Squared Error for Model {i}')
        plt.ylabel('Mean Squared Error')
        plt.xlabel('Epoch')

        plt.legend()
        plt.show()
        plt.savefig(F"models\MSEModelPlot{i}.png")
        plt.clf()

    end_time = time.time()

    print(F"Time to complete: {end_time - start_time} seconds\n")
