import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers
import time
import matplotlib.pyplot as plt

from data_manager import process_data, test_train_split, gen_lstm_inputs, gen_categorical, augment_append_data

params = {
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
    "dropout": 0.0,
    "output_activation": "tanh",
}


def get_uncompiled_lstm(input_size):
    """ Input shapes: (batches, timesteps, features). """
    inputs = keras.Input(shape=input_size, name="scan")
    x = layers.ConvLSTM2D(1, (2, 2), padding="same",
                          activation="relu")(inputs)

    x = layers.Conv2D(16, (5, 5), padding="same", activation="relu")(x)
    x = layers.MaxPooling2D(pool_size=(2, 2))(x)
    x = layers.Flatten()(x)
    # x = layers.Dense(2, activation="relu", name="dense_6")(x)
    # output_x = layers.Dense(1, activation="linear", name="predictions_x")(x)
    output_x = layers.Dense(2, activation="tanh", name="predictions_x")(x)
    model = keras.Model(inputs=inputs, outputs=output_x)
    return model


def get_compiled_cnn(params):
    activation = params["activation"]
    padding = params["padding"]
    reg = params["regularizer"]
    scan_input = keras.Input(shape=params["scan_shape"], name="scan_input")
    img_input = keras.Input(shape=params["img_shape"], name="image_input")

    # Process Scan input.
    x_scan = layers.Conv2D(params["conv1n"],
                           params["conv1f"],
                           strides=params["conv1s"],
                           padding=padding,
                           activation=activation,
                           name="conv1")(scan_input)
    # x_scan = layers.Dropout(0.2)(x_scan)
    x_scan = layers.MaxPooling2D(
        pool_size=params["pool1s"], name="pool1")(x_scan)
    # x_scan = layers.Dense(16, activation=activation)(x_scan)
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
    # x_img = layers.Dropout(0.25)(x_img)
    x_img = layers.Conv2D(params["conv3n"], 
                          params["conv3f"], 
                          strides=params["conv3s"],
                          padding=padding,
                          activation=activation, 
                          name="conv3")(img_input)
    x_img = layers.AveragePooling2D(pool_size=3)(x_img)
    # x_img = layers.Dropout(0.1)(x_img)
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

    # Concatenate inputs to singular tensor.
    x = layers.Concatenate(axis=1)([x_scan, x_img])

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
    model = keras.Model(inputs=[scan_input, img_input], outputs=output_x)

    model.compile(
        # optimizer=keras.optimizers.Adadelta(),  # Optimizer
        optimizer=keras.optimizers.Adam(learning_rate=0.0001),  # Optimizer
        # optimizer="RMSprop",
        # optimizer=tf.keras.optimizers.SGD(),
        # Loss function to minimize
        # loss="mae",
        # loss=tf.keras.losses.CosineSimilarity(),
        # loss=tf.keras.losses.MeanSquaredLogarithmicError(),
        # loss=tf.keras.losses.LogCosh(),  # Best so far.
        loss=tf.keras.losses.MeanSquaredError(),
        # loss=keras.losses.MeanAbsoluteError(),
        # loss=tf.keras.losses.Huber(),
        # loss=tf.keras.losses.MeanSquaredError(),
        # List of metrics to monitor
        metrics=[
            tf.keras.metrics.MeanAbsoluteError(),
            # tf.keras.metrics.MeanSquaredError(),
        ],
    )
    return model


# def get_compiled_model(to_compile="", input_size=(32, 32, 1)):
    # if to_compile == "cnn":
    #     model = get_uncompiled_cnn(input_size)
    # elif to_compile == "lstm":
    #     model = get_uncompiled_lstm(input_size)
    # else:
    #     raise TypeError("What model to compile? (cnn/lstm/...")

    # model.compile(
    #     # optimizer=keras.optimizers.Adadelta(),  # Optimizer
    #     optimizer=keras.optimizers.Adam(learning_rate=0.0001),  # Optimizer
    #     # optimizer="RMSprop",
    #     # optimizer="Ftrl",
    #     # optimizer="Nadam",
    #     # optimizer=tf.keras.optimizers.SGD(),
    #     # Loss function to minimize
    #     # loss="mae",
    #     # loss=tf.keras.losses.CosineSimilarity(),
    #     # loss=tf.keras.losses.MeanSquaredLogarithmicError(),
    #     loss=tf.keras.losses.LogCosh(),  # Best so far.
    #     # loss=tf.keras.losses.Huber(),
    #     # loss=tf.keras.losses.MeanSquaredError(),
    #     # List of metrics to monitor
    #     metrics=[
    #         # tf.keras.metrics.MeanAbsoluteError(),
    #         tf.keras.metrics.MeanSquaredError(),
    #         # tf.keras.metrics.MeanSquaredLogarithmicError(),
    #     ],
    # )

    # return model


def main_lstm(x_data, y_data):
    lstm_in, lstm_out = gen_lstm_inputs(x_data, y_data, 4, 4)
    image_shape = lstm_in.shape[1:]
    print(F"Image Shape: {image_shape}\n")

    x_train, y_train = lstm_in[:-1000], lstm_out[:-1000]
    x_test, y_test = lstm_in[-1000:], lstm_out[-1000:]

    model = get_compiled_model(to_compile="lstm", input_size=image_shape)
    return model


def main_cnn(x_data, y_data):
    image_shape = x_data.shape[1:]
    return model


def main_categorical(x_data, num_classes):
    input_size = x_data.shape[1:]
    inputs = keras.Input(shape=input_size, name="scan")
    x = layers.Conv2D(1, (2, 2), padding="same", activation="relu")(inputs)
    x = layers.AveragePooling2D(pool_size=(2, 2))(x)
    # x = layers.Conv2D(2, (2, 2), padding="same", activation="relu")(x)
    # x = layers.AveragePooling2D(pool_size=(2, 2))(x)
    x = layers.Flatten()(x)
    output_x = layers.Dense(
        num_classes+1, activation="softmax", name="pred_x")(x)
    output_y = layers.Dense(
        num_classes+1, activation="softmax", name="pred_y")(x)

    model = keras.Model(inputs=inputs, outputs=[output_x, output_y])

    model.compile(
        # optimizer=keras.optimizers.Adadelta(),  # Optimizer
        optimizer=keras.optimizers.Adam(),  # Optimizer
        # optimizer="RMSprop",
        # optimizer="Ftrl",
        # optimizer="Nadam",
        # optimizer=tf.keras.optimizers.SGD(),
        # Loss function to minimize
        # loss=tf.keras.losses.CategoricalCrossentropy(),
        loss=tf.keras.losses.BinaryCrossentropy(),
        # List of metrics to monitor
        # metrics=[tf.keras.metrics.MeanAbsoluteError()],
        metrics=[tf.keras.metrics.CategoricalCrossentropy(), ],
    )

    return model


if __name__ == "__main__":
    start_time = time.time()

    img_size = 64
    batch_size = 128
    num_epochs = 100

    path_to_train = "python\DriverTraining\ScanData\ImgScanData_training.csv"
    path_to_train_no_img = "python\DriverTraining\ScanData\OldScans\TrainingData.csv"
    path_to_test = "python\DriverTraining\ScanData\CSUArtScan.csv"
    path_to_test_no_img = "python\DriverTraining\ScanData\OldScans\TestData.csv"

    x_scan_train, x_img_train, y_train = process_data(
        path_to_train, scan_img_size=img_size)
    x_scan_test, x_img_test, y_test = process_data(
        path_to_test, scan_img_size=img_size)
    x_scan_train_gen, x_img_train_gen, y_train_gen = process_data(
        path_to_train_no_img, scan_img_size=img_size, no_img=True)
    # x_scan_test_gen, x_img_test_gen, y_test_gen = process_data(
    #     path_to_test_no_img, scan_img_size=img_size, no_img=True)

    x_scan_train = np.append(x_scan_train, x_scan_train_gen, axis=0)
    x_img_train = np.append(x_img_train, x_img_train_gen, axis=0)
    y_train = np.append(y_train, y_train_gen, axis=0)

    # x_scan_test = np.append(x_scan_test, x_scan_test_gen, axis=0)
    # x_img_test = np.append(x_img_test, x_img_test_gen, axis=0)
    # y_test = np.append(y_test, y_test_gen, axis=0)

    x_scan_train, x_img_train, y_train = augment_append_data(
        x_scan_train, x_img_train, y_train)
    x_scan_test, x_img_test, y_test = augment_append_data(
        x_scan_test, x_img_test, y_test)

    scan_val, img_val, y_val, scan_train, img_train, y_train = test_train_split(
        x_scan_train, x_img_train, y_train)

    param_test_list = []
    param_test_0 = params.copy()
    param_test_0["activation"] = "relu"
    param_test_0["conv1n"] = 64  # Conv on scan image.
    param_test_0["conv2n"] = 128
    param_test_0["conv3n"] = 256
    param_test_0["conv4n"] = 256
    param_test_0["conv1f"] = 1
    param_test_0["conv2f"] = 1
    param_test_0["conv3f"] = 1
    param_test_0["conv4f"] = 1
    # param_test_0["conv1s"] = 3
    # param_test_0["conv2s"] = 3
    # param_test_0["conv3s"] = 3
    # param_test_0["conv4s"] = 3
    param_test_0["pool1s"] = 6
    param_test_0["pool2s"] = 6
    param_test_0["pool3s"] = 6
    param_test_0["dense1n"] = 1028
    param_test_0["dense2n"] = 128
    param_test_0["dropout"] = 0.5
    param_test_list.append(param_test_0)

    """Winning paramaters so far."""
    param_test_1 = params.copy()
    param_test_1["activation"] = "relu"
    param_test_1["conv1n"] = 32  # Conv on scan image.
    param_test_1["conv2n"] = 64
    param_test_1["conv3n"] = 128
    param_test_1["conv4n"] = 256
    param_test_1["conv1f"] = 1
    param_test_1["conv2f"] = 1
    param_test_1["conv3f"] = 1
    param_test_1["conv4f"] = 1
    param_test_1["pool1s"] = 6
    param_test_1["pool2s"] = 6
    param_test_1["pool3s"] = 6
    param_test_1["dense1n"] = 1028
    param_test_1["dense2n"] = 128
    param_test_1["dropout"] = 0.5
    param_test_list.append(param_test_1)

    param_test_2 = params.copy()
    param_test_2["activation"] = "relu"
    param_test_2["conv1n"] = 32  # Conv on scan image.
    param_test_2["conv2n"] = 64
    param_test_2["conv3n"] = 128
    param_test_2["conv4n"] = 256
    param_test_2["conv1f"] = 1
    param_test_2["conv2f"] = 1
    param_test_2["conv3f"] = 1
    param_test_2["conv4f"] = 1
    param_test_2["pool1s"] = 6
    param_test_2["pool2s"] = 6
    param_test_2["pool3s"] = 6
    param_test_2["dense1n"] = 1028
    param_test_2["dense2n"] = 1028
    param_test_2["dropout"] = 0.5
    param_test_list.append(param_test_2)

    # param_test_3 = params.copy()
    # param_test_3["activation"] = "tanh"
    # param_test_3["conv1n"] = 16  # Conv on scan image.
    # param_test_3["conv2n"] = 64
    # param_test_3["conv3n"] = 128
    # param_test_3["conv4n"] = 256
    # param_test_3["conv1s"] = 1
    # param_test_3["conv2s"] = 1
    # param_test_3["conv3s"] = 1
    # param_test_3["conv4s"] = 1
    # param_test_3["pool1s"] = 6
    # param_test_3["pool2s"] = 6
    # param_test_3["pool3s"] = 6
    # param_test_3["dense1n"] = 1028
    # param_test_3["dense2n"] = 128
    # param_test_3["dropout"] = 0.5
    # param_test_list.append(param_test_3)

    # param_test_4 = params.copy()
    # param_test_4["activation"] = "tanh"
    # param_test_4["conv1n"] = 8  # Conv on scan image.
    # param_test_4["conv2n"] = 64
    # param_test_4["conv3n"] = 128
    # param_test_4["conv4n"] = 256
    # param_test_4["conv1s"] = 1
    # param_test_4["conv2s"] = 1
    # param_test_4["conv3s"] = 1
    # param_test_4["conv4s"] = 1
    # param_test_4["pool1s"] = 6
    # param_test_4["pool2s"] = 6
    # param_test_4["pool3s"] = 6
    # param_test_4["dense1n"] = 1028
    # param_test_4["dense2n"] = 128
    # param_test_4["dropout"] = 0.5
    # param_test_list.append(param_test_4)

    # param_test_5 = params.copy()
    # param_test_5["activation"] = None
    # param_test_5["conv1n"] = 16  # Conv on scan image.
    # param_test_5["conv2n"] = 64
    # param_test_5["conv3n"] = 128
    # param_test_5["conv4n"] = 256
    # param_test_5["conv1s"] = 1
    # param_test_5["conv2s"] = 1
    # param_test_5["conv3s"] = 1
    # param_test_5["conv4s"] = 1
    # param_test_5["pool1s"] = 6
    # param_test_5["pool2s"] = 6
    # param_test_5["pool3s"] = 6
    # param_test_5["dense1n"] = 1028
    # param_test_5["dense2n"] = 128
    # param_test_5["dropout"] = 0.5
    # param_test_list.append(param_test_5)

    # param_test_6 = params.copy()
    # param_test_6["activation"] = None
    # param_test_6["conv1n"] = 8  # Conv on scan image.
    # param_test_6["conv2n"] = 64
    # param_test_6["conv3n"] = 128
    # param_test_6["conv4n"] = 256
    # param_test_6["conv1s"] = 1
    # param_test_6["conv2s"] = 1
    # param_test_6["conv3s"] = 1
    # param_test_6["conv4s"] = 1
    # param_test_6["pool1s"] = 6
    # param_test_6["pool2s"] = 6
    # param_test_6["pool3s"] = 6
    # param_test_6["dense1n"] = 1028
    # param_test_6["dense2n"] = 128
    # param_test_6["dropout"] = 0.5
    # param_test_list.append(param_test_6)

    # param_test_3 = params.copy()
    # param_test_3["activation"] = "relu"
    # param_test_3["conv1n"] = 8  # Conv on scan image.
    # param_test_3["conv2n"] = 64
    # param_test_3["conv3n"] = 128
    # param_test_3["conv4n"] = 256
    # param_test_3["pool3s"] = 6
    # param_test_3["dense1n"] = 1028
    # param_test_3["dense2n"] = 128
    # param_test_list.append(param_test_3)

    # param_test_4 = params.copy()
    # param_test_4["activation"] = "relu"
    # param_test_4["conv1n"] = 8  # Conv on scan image.
    # param_test_4["conv2n"] = 64
    # param_test_4["conv3n"] = 128
    # param_test_4["conv4n"] = 256
    # param_test_4["pool3s"] = 6
    # param_test_4["dense1n"] = 2048
    # param_test_4["dense2n"] = 1024
    # param_test_4["dense3n"] = 512
    # param_test_4["dense4n"] = 512
    # param_test_4["dense5n"] = 512
    # param_test_4["dense6n"] = 512
    # param_test_list.append(param_test_4)

    # Append default group to end, acts as control group.
    param_test_list.append(params.copy())  # Default settings.

    # for parameters in param_test_list:
    for i in range(0, len(param_test_list)):
        print(F"*\n*\n*\n\tTesting Model no. {i}\n*\n*\n*")
        parameters = param_test_list[i]
        model = get_compiled_cnn(parameters)
        # keras.utils.plot_model(model , to_file=F"models\modelArch{i}.png")
        model.summary()
        my_callbacks = [keras.callbacks.EarlyStopping(patience=3)]

        # train_again = 'y'
        # while (train_again == 'y'):
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

        # print(history.history.keys())
        # summarize history for loss

        fig, ax = plt.subplots()

        major_ticks = np.arange(0.00, 0.25, 0.05)
        minor_ticks = np.arange(0.0, 0.24, 0.01)
        ax.set_yticks(major_ticks, minor=False)
        ax.set_yticks(minor_ticks, minor=True)
        ax.yaxis.grid(True, which='major')
        ax.yaxis.grid(True, which='minor')

        test_mae_line, = ax.plot([0, len(history.history['loss'])],
                                 [results[1], results[1]])
        test_loss_line, = ax.plot([0, len(history.history['loss'])], 
                                  [results[0], results[0]])
        val_mae_line, = ax.plot(history.history['val_mean_absolute_error'])
        val_loss_line, = ax.plot(history.history['val_loss'])
        mae_line, = ax.plot(history.history['mean_absolute_error'])
        loss_line, = ax.plot(history.history['loss'])

        plt.title(F'Metrics for Model {i}')
        plt.ylabel('loss')
        plt.xlabel('epoch')
        plt.legend((loss_line, mae_line, val_loss_line, val_mae_line, test_loss_line, test_mae_line),
                   ('train loss', 'train mae', 'val loss', 'val mae', 'test loss', 'test mae'))
        # plt.legend((),('train_loss', 'val_loss', 'test_loss','mse', 'val_mse', 'test_mse'))
        # plt.show()

        plt.savefig(F"models\modelPlot{i}.png")
        plt.clf()

    # print(history.history.keys())
    # summarize history for loss

    # print("\nEvaluate on test data.\n")
    # results = model.evaluate(
    #     [x_scan_test, x_img_test], y_test, batch_size=batch_size)
    # print(F"Results: {results}\n")

    # save = input("Would you like to save the model? (y/n): ")

    # if save == 'y':
    #     model.save("python/DriverTraining/trained_model.h5")
    #     print("Saved Model!")

    end_time = time.time()

    print(F"Time to complete: {end_time - start_time} seconds\n")
