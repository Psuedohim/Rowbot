import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
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
    inputs = keras.Input(shape=input_size, name="scan")
    x = layers.Conv2D(1, (2, 2), padding="same", activation="relu")(inputs)
    x = layers.AveragePooling2D(pool_size=(2, 2))(x)
    x = layers.Conv2D(2, (2, 2), padding="same", activation="relu")(x)
    x = layers.AveragePooling2D(pool_size=(2, 2))(x)
    x = layers.Flatten()(x)
    # x = layers.Dense(64, activation="tanh", name="dense_5")(x)
    # x = layers.Dense(2, activation="relu", name="dense_6")(x)
    # output_x = layers.Dense(1, activation="linear", name="predictions_x")(x)
    output_x = layers.Dense(2, activation="tanh", name="predictions_x")(x)
    model = keras.Model(inputs=inputs, outputs=output_x)
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
        # optimizer=keras.optimizers.Adam(),  # Optimizer
        # optimizer="RMSprop",
        # optimizer="Ftrl",
        optimizer="Nadam",
        # optimizer=tf.keras.optimizers.SGD(),
        # Loss function to minimize
        # loss="mse",
        # loss=tf.keras.losses.MeanAbsolutePercentageError(),
        # loss=tf.keras.losses.CosineSimilarity(),
        # loss=tf.keras.losses.MeanSquaredLogarithmicError(),
        loss=tf.keras.losses.LogCosh(),  # Best so far.
        # loss=tf.keras.losses.Huber(),
        # loss=tf.keras.losses.MeanSquaredError(),
        # List of metrics to monitor
        # metrics=[tf.keras.metrics.MeanAbsoluteError()],
        metrics=[tf.keras.metrics.Accuracy(),
                 tf.keras.metrics.MeanAbsoluteError(),
                 tf.keras.metrics.MeanSquaredError()],
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
    path_to_data = "python/DriverTraining/ScanData/TrainingData.csv"

    x_data, y_data = process_data(path_to_data, img_size=64)
    model = main_categorical(x_data, 20)
    y_data = gen_categorical(y_data, 20)

    test_size = 2500

    x_train = x_data[:-test_size]
    y_train = y_data[:-test_size]

    x_test = x_data[-test_size:]
    y_test = y_data[-test_size:]

    # model = main_cnn(x_data, y_data)
    # model = main_lstm(x_data, y_data)

    model.summary()
    print(F"x 1-hot: {y_train[:,0].shape}\n")
    print(F"y 1-hot: {y_train[:,1].shape}\n")

    print("Fit model on training data")
    history = model.fit(
        x_train,
        [y_train[:, 0], y_train[:, 1]],
        batch_size=32,
        epochs=30,
        verbose=1,
    )

    print("Evaluate on test data")
    results = model.evaluate(
        x_test, [y_test[:, 0], y_test[:, 1]], batch_size=32)
    print(F"Results: {results}\n")

    x_to_show = np.zeros((1, 64, 64, 1))

    x_to_show[0, :] = x_test[0]
    y_to_show = y_test[0]
    pred1, pred2 = model.predict(x_to_show)

    print(F"Actual: {y_to_show}\n")
    print(F"Predicted: {pred1}\n{pred2}\n")

    model.save("python/DriverTraining/trained_model.h5")
    print("Saved Model!")
    end_time = time.time()

    print(F"Time to complete: {end_time - start_time} seconds\n")
