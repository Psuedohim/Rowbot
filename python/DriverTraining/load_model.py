# load and evaluate a saved model
from tensorflow.keras.models import load_model
from data_manager import process_data, test_train_split

# load model
model = load_model('python/DriverTraining/trained_model.h5')
# summarize model.
model.summary()

# path_to_data = "python/DriverTraining/ScanData/OrigHouseScan1.csv"
path_to_data = "python/DriverTraining/ScanData/BetterData.csv"

x_data, y_data = process_data(path_to_data)
x_test, x_train, y_test, y_train = test_train_split(
    x_data, y_data, test_size=200)

predictions = model.predict(x_test)
print(predictions * 90)
