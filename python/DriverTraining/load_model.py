# load and evaluate a saved model
from tensorflow.keras.models import load_model
from data_manager import process_data, test_train_split

# load model
model = load_model('python/DriverTraining/trained_model.h5')
# summarize model.
# model.summary()

# path_to_train = "python/DriverTraining/ScanData/BetterData.csv"
path_to_train = "python/DriverTraining/ScanData/RetrainingData.csv"

test_paths = [
    "python/DriverTraining/ScanData/HallwayMaze1.csv",
    "python/DriverTraining/ScanData/HallwayMaze2.csv",
    "python/DriverTraining/ScanData/HallwayMaze3.csv",
    "python/DriverTraining/ScanData/HallwayMazeFullSpeed.csv",
    "python/DriverTraining/ScanData/BetterData.csv"
]

x_data, y_data = process_data(path_to_train, 32)
print(F"X_data.shape: {x_data.shape}")
_, x_train, _, y_train = test_train_split(
    x_data, y_data, test_size=100)


def run_tests():
    for path in test_paths:
        test_x, test_y = process_data(path, 32)
        _, x_test, _, y_test = test_train_split(
            test_x, test_y, test_size=1)
        results = model.evaluate(x_test, y_test, batch_size=128)
        print(F"Results from {path}\n\t{results}\n")


print(F"Shape of Train set: {x_train.shape}\n")

while True:

    again = input("Would you like to train the model? (y/n): ")
    if again == 'y':
        epochs = int(input("How many epochs? "))

        print("Fit model on training data")
        history = model.fit(
            x_train,
            y_train,
            batch_size=128,
            epochs=epochs,
            verbose=1,
        )

    run_tests()

    save = input("\nWould you like to save the model at this time? (y/n)")
    if save == "y":
        model.save("python/DriverTraining/trained_model.h5")
        print("Saved Model!")
        break
