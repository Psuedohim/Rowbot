import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import time

from data_manager import process_data, test_train_split


def get_uncompiled_model(input_size):
    inputs = keras.Input(shape=input_size, name="scan")
    x = layers.Conv2D(64, (7, 7), padding="same", activation="relu")(inputs)
    x = layers.MaxPooling2D(pool_size=(2, 2))(x)
    # x = layers.Conv2D(64, (5, 5), padding="same", activation="relu")(x)
    # x = layers.MaxPooling2D(pool_size=(2, 2))(x)
    # x = layers.Conv2D(128, (5, 5), padding="same", activation="relu")(x)
    # x = layers.MaxPooling2D(pool_size=(2, 2))(x)
    # x = layers.Conv2D(512, (5, 5), padding="same", activation="relu")(x)
    # x = layers.MaxPooling2D(pool_size=(2, 2))(x)
    # x = layers.Dense(1024, activation="relu", name="dense_1")(inputs)
    x = layers.Flatten()(x)
    # x = layers.Dense(512, activation="relu", name="dense_2")(x)
    # x = layers.Dense(256, activation="relu", name="dense_3")(x)
    # x = layers.Dense(128, activation="relu", name="dense_4")(x)
    x = layers.Dense(64, activation="relu", name="dense_5")(x)
    x = layers.Dense(32, activation="relu", name="dense_6")(x)
    # output_x = layers.Dense(1, activation="linear", name="predictions_x")(x)
    output_x = layers.Dense(1, activation="tanh", name="predictions_x")(x)
    model = keras.Model(inputs=inputs, outputs=output_x)
    return model


def get_compiled_model(input_size=(32, 32, 1)):
    model = get_uncompiled_model(input_size)
    model.compile(
        # optimizer=keras.optimizers.Adadelta(),  # Optimizer
        optimizer=keras.optimizers.Adam(),  # Optimizer
        # Loss function to minimize
        # loss="cosine_similarity",
        loss="mse",
        # loss=tf.keras.losses.MeanSquaredError(),
        # List of metrics to monitor
        # metrics=[tf.keras.metrics.MeanAbsoluteError()],
        metrics=[tf.keras.metrics.RootMeanSquaredError()],
    )
    return model


if __name__ == "__main__":
    start_time = time.time()
    # path_to_data = "python/DriverTraining/ScanData/OrigHouseScan1.csv"
    path_to_data = "python/DriverTraining/ScanData/BetterData.csv"

    x_data, y_data = process_data(path_to_data)
    x_test, x_train, y_test, y_train = test_train_split(
        x_data, y_data, test_size=3000)

    image_shape = x_test.shape[1:]
    print(image_shape)

    model = get_compiled_model(input_size=image_shape)
    model.summary()

    print("Fit model on training data")
    history = model.fit(
        x_train,
        y_train,
        batch_size=256,
        epochs=10,
        verbose=1,
    )

    history.history
    # Evaluate the model on the test data using `evaluate`
    print("Evaluate on test data")
    results = model.evaluate(x_test, y_test, batch_size=100)
    print(F"Results: {results}\n")

    model.save("python/DriverTraining/trained_model.h5")
    print("Saved Model!")
    end_time = time.time()

    print(F"Time to complete: {end_time - start_time} seconds\n")
