import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers
import time
import matplotlib.pyplot as plt

from data_manager import process_data, test_train_split, gen_lstm_inputs, gen_categorical


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


def get_uncompiled_cnn(input_size):
    activation = "relu"
    reg = regularizers.l1(0.0001)
    scan_input = keras.Input(shape=input_size, name="scan")
    img_input = keras.Input(shape=(80, 128, 1), name="image")
    # Process Scan input.
    x_scan = layers.Conv2D(1, 3, padding="same",
                           activation=activation)(scan_input)
    x_scan = layers.Dropout(0.2)(x_scan)
    x_scan = layers.MaxPooling2D(pool_size=2)(x_scan)
    x_scan = layers.Dense(16, activation=activation)(x_scan)
    x_scan = layers.Flatten()(x_scan)

    # Process Image input.
    x_img = layers.Conv2D(16, 3, padding="same",
                          activation=activation)(img_input)
    x_img = layers.MaxPooling2D(pool_size=2)(x_img)
    x_img = layers.Dropout(0.25)(x_img)
    x_img = layers.Conv2D(3, 5, padding="same",
                          activation=activation)(x_img)
    x_img = layers.MaxPooling2D(pool_size=2)(x_img)
    # x_img = layers.Dropout(0.1)(x_img)
    x_img = layers.Conv2D(3, 7, padding="same",
                          activation=activation,
                          activity_regularizer=reg)(x_img)
    x_img = layers.AveragePooling2D(pool_size=2)(x_img)
    # x_img = layers.Dropout(0.1)(x_img)
    # x_img = layers.Conv2D(64, 3, padding="valid", activation=activation)(x_img)
    # x_img = layers.MaxPooling2D(pool_size=2)(x_img)
    # x_img = layers.Dropout(0.2)(x_img)
    # x_img = layers.Conv2D(128, 5, padding="valid",
    #                       activation=activation)(x_img)
    # x_img = layers.MaxPooling2D(pool_size=2)(x_img)
    # x_img = layers.Dropout(0.2)(x_img)
    # x_img = layers.Conv2D(512, 5, padding="same", activation=activation)(x_img)
    # x_img = layers.AveragePooling2D(pool_size=2)(x_img)
    # x_img = layers.Dropout(0.2)(x_img)
    x_img = layers.Dense(16, activation=activation)(x_img)
    x_img = layers.Flatten()(x_img)

    # Concatenate inputs to singular tensor.
    x = layers.Concatenate(axis=1)([x_scan, x_img])

    # x = layers.Dropout(0.1)(x)
    # x = layers.Dropout(0.2)(x)
    # x = layers.Dense(1028, activation="relu", name="dense_1")(x)
    # x = layers.Dense(1028, activation="relu", name="dense_1_1")(x)
    # x = layers.Dense(256, activation=activation, name="dense_2")(x)
    # x = layers.Dense(128, activation=activation, name="dense_3")(x)
    # x = layers.Dense(64, activation=activation, name="dense_4")(x)
    x = layers.Dense(32, activation=activation,
                     name="dense_5", activity_regularizer=reg)(x)
    x = layers.Dense(4, activation=activation, name="dense_6",
                     activity_regularizer=reg)(x)
    x = layers.Dense(4, activation=activation, name="dense_7",
                     activity_regularizer=reg)(x)
    output_x = layers.Dense(2, activation="tanh",
                            name="x_y_out")(x)  # Tanh: [-1, 1]
    model = keras.Model(inputs=[scan_input, img_input], outputs=output_x)
    return model


def get_compiled_model(to_compile="", input_size=(32, 32, 1)):
    if to_compile == "cnn":
        model = get_uncompiled_cnn(input_size)
    elif to_compile == "lstm":
        model = get_uncompiled_lstm(input_size)
    else:
        raise TypeError("What model to compile? (cnn/lstm/...")

    model.compile(
        # optimizer=keras.optimizers.Adadelta(),  # Optimizer
        optimizer=keras.optimizers.Adam(learning_rate=0.0001),  # Optimizer
        # optimizer="RMSprop",
        # optimizer="Ftrl",
        # optimizer="Nadam",
        # optimizer=tf.keras.optimizers.SGD(),
        # Loss function to minimize
        # loss="mae",
        # loss=tf.keras.losses.CosineSimilarity(),
        # loss=tf.keras.losses.MeanSquaredLogarithmicError(),
        loss=tf.keras.losses.LogCosh(),  # Best so far.
        # loss=tf.keras.losses.Huber(),
        # loss=tf.keras.losses.MeanSquaredError(),
        # List of metrics to monitor
        metrics=[
            # tf.keras.metrics.MeanAbsoluteError(),
            tf.keras.metrics.MeanSquaredError(),
            # tf.keras.metrics.MeanSquaredLogarithmicError(),
        ],
    )

    return model


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
    num_epochs = 50

    path_to_train = "python\DriverTraining\ScanData\ImgScanData_training.csv"
    path_to_train_no_img = "python\DriverTraining\ScanData\OldScans\TrainingData.csv"
    path_to_test = "python\DriverTraining\ScanData\ImgScanData_testing.csv"
    path_to_test_no_img = "python\DriverTraining\ScanData\OldScans\TestData.csv"

    x_scan_train, x_img_train, y_train = process_data(
        path_to_train, scan_img_size=img_size)
    x_scan_test, x_img_test, y_test = process_data(
        path_to_test, scan_img_size=img_size)
    x_scan_train_gen, x_img_train_gen, y_train_gen = process_data(
        path_to_train_no_img, scan_img_size=img_size, no_img=True)
    x_scan_test_gen, x_img_test_gen, y_test_gen = process_data(
        path_to_test_no_img, scan_img_size=img_size, no_img=True)

    x_scan_train = np.append(x_scan_train, x_scan_train_gen, axis=0)
    x_img_train = np.append(x_img_train, x_img_train_gen, axis=0)
    y_train = np.append(y_train, y_train_gen, axis=0)

    x_scan_test = np.append(x_scan_test, x_scan_test_gen, axis=0)
    x_img_test = np.append(x_img_test, x_img_test_gen, axis=0)
    y_test = np.append(y_test, y_test_gen, axis=0)

    model = get_compiled_model(
        to_compile="cnn", input_size=x_scan_train.shape[1:])
    # x_test, x_train, y_test, y_train = test_train_split(
    #     x_data, y_data, test_size=1000)
    # model = main_categorical(x_data, 20)
    # y_data = gen_categorical(y_data, 20)

    # test_size = 2500

    # x_train = x_data[:-test_size]
    # y_train = y_data[:-test_size]

    # x_test = x_data[-test_size:]
    # y_test = y_data[-test_size:]

    model.summary()
    # print(F"x 1-hot: {y_train[:,0].shape}\n")
    # print(F"y 1-hot: {y_train[:,1].shape}\n")

    train_again = 'y'
    while (train_again == 'y'):
        print("Fit model on training data")
        history = model.fit(
            [x_scan_train, x_img_train],
            y_train,
            batch_size=batch_size,
            epochs=num_epochs,
            validation_data=([x_scan_test, x_img_test], y_test),
            verbose=1,
        )

        print(history.history.keys())
        # summarize history for loss
        plt.plot(history.history['loss'])
        plt.plot(history.history['val_loss'])
        plt.plot(history.history['mean_squared_error'])
        plt.plot(history.history['val_mean_squared_error'])
        plt.title('model loss')
        plt.ylabel('loss')
        plt.xlabel('epoch')
        plt.legend(['train', 'test', 'mse', 'val_mse'], loc='upper left')
        plt.show()
        train_again = input("Train again? (y/n): ")

    # print(history.history.keys())
    # summarize history for loss

    # print("\nEvaluate on test data.\n")
    # results = model.evaluate(
    #     [x_scan_test, x_img_test], y_test, batch_size=batch_size)
    # print(F"Results: {results}\n")

    save = input("Would you like to save the model? (y/n): ")

    if save == 'y':
        model.save("python/DriverTraining/trained_model.h5")
        print("Saved Model!")

    # plt.plot(history.history['loss'])
    # plt.plot(history.history['val_loss'])
    # plt.plot(history.history['mean_squared_error'])
    # plt.plot(history.history['val_mean_squared_error'])
    # plt.title('model loss')
    # plt.ylabel('loss')
    # plt.xlabel('epoch')
    # plt.legend(['train', 'test', 'mse', 'val_mse'], loc='upper left')
    # plt.show()

    end_time = time.time()

    print(F"Time to complete: {end_time - start_time} seconds\n")
