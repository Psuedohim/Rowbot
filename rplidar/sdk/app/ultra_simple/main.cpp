#include <bits/stdc++.h> 
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <iostream>
#include <fstream>
#include <cmath>
#include <i2c_comm.h>
#include <fdeep/fdeep.hpp>
#include <rplidar.h> //RPLIDAR standard sdk, all-in-one header
#include <opencv2/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/videoio.hpp>


using namespace rp::standalone::rplidar;

RPlidarDriver *driver; // Initialize pointer for LiDAR driver.
u_result op_result;

#ifndef _countof
#define _countof(_Array) (int)(sizeof(_Array) / sizeof(_Array[0]))
#endif

bool ctrl_c_pressed;
bool PREV_AUTO_STATE;
bool PREV_SAVE_STATE;
bool LIDAR_ALREADY_SETUP = false;
I2C_IN_PACK MCU_PACKAGE;
I2C_OUT_PACK DRIVE_INSTR;

std::ofstream CSV_FILE; // For saving scan data.
cv::VideoCapture cap("/dev/video0");  // Initialize RPi Camera reader.

struct DataToSave
{
	bool invalid_data = false;
	std::vector<float> theta_deg;
	std::vector<float> distance_mm;
	int8_t joystick_x;
	int8_t joystick_y;
};

void
ctrlc(int)
{
	/* This method is called when the user exits the program via `ctrl-c`.
	 * This will set a global variable, ctrl-c-pressed, to true, causing a 
	 * break in the control loop. 
	 */
	ctrl_c_pressed = true;
}

bool checkRPLIDARHealth(RPlidarDriver *driver)
{
	/* This method collects the current health information from the RPLiDAR 
	 * device. 
	 * Returns:
	 * 		true - Device is okay, ready to go.
	 * 		false - Device could not be connected to / Device not in good health.
	 */
	u_result op_result;
	rplidar_response_device_health_t healthinfo;

	op_result = driver->getHealth(healthinfo);
	if (IS_OK(op_result))
	{
		printf("RPLidar health status : %d\n", healthinfo.status);
		if (healthinfo.status == RPLIDAR_STATUS_ERROR)
		{
			fprintf(stderr, "Error, rplidar internal error detected. Please reboot the device to retry.\n");
			// enable the following code if you want rplidar to be reboot by software
			// driver->reset();
			return false;
		}
		else
		{
			return true;
		}
	}
	else
	{
		fprintf(stderr, "Error, cannot retrieve the lidar health code: %x\n", op_result);
		return false;
	}
}

void setup_lidar()
{
	/* Runs setup routine for RPLiDAR.
	 * Assigns global pointer, `driver`, to an instance of RPLiDAR driver on
	 * the specified port with baudrate 115200; the baudrate for RPLiDAR A2.
	 */
	// if (LIDAR_ALREADY_SETUP)
	// 	return;

	const char *opt_com_path = NULL;
	opt_com_path = "/dev/ttyUSB0";

	// Create the driver instance.
	driver = RPlidarDriver::CreateDriver(DRIVER_TYPE_SERIALPORT);
	if (!driver) // If driver creation was not successful,
	{
		fprintf(stderr, "insufficent memory, exit\n");
		exit(-2);
	}

	rplidar_response_device_info_t devinfo;
	bool connectSuccess = false;
	// make connection...
	driver = RPlidarDriver::CreateDriver(DRIVER_TYPE_SERIALPORT);
	if (IS_OK(driver->connect(opt_com_path, 115200)))
	{
		op_result = driver->getDeviceInfo(devinfo);

		if (IS_OK(op_result))
		{
			connectSuccess = true;
		}
		else
		{
			delete driver;
			driver = NULL;
		}
	}

	if (!connectSuccess)
	{
		fprintf(stderr, "Error, cannot bind to the specified serial port %s.\n", opt_com_path);

		RPlidarDriver::DisposeDriver(driver);
		driver = NULL;
	}

	// print out the device serial number, firmware and hardware version number..
	printf("RPLIDAR S/N: ");
	for (int pos = 0; pos < 16; ++pos)
	{
		printf("%02X", devinfo.serialnum[pos]);
	}

	printf("\n"
				 "Firmware Ver: %d.%02d\n"
				 "Hardware Rev: %d\n",
				 devinfo.firmware_version >> 8, devinfo.firmware_version & 0xFF, (int)devinfo.hardware_version);

	// check health...
	if (!checkRPLIDARHealth(driver))
	{
		RPlidarDriver::DisposeDriver(driver);
		driver = NULL;
	}
	driver->startMotor();
	// Setup for scan process.
	std::vector<RplidarScanMode> scanModes;
	driver->getAllSupportedScanModes(scanModes);
	driver->startScanExpress(false, scanModes[1].id);

	LIDAR_ALREADY_SETUP = true;
}

void shutdown_lidar()
{
	driver->stop();			 // Stop scanning.
	driver->stopMotor(); // Stop spinning RPLiDAR motor.
}

DataToSave get_lidar_data()
{
	/*
	Retrieve a scan from the LiDAR.
	Format scan into series of two vectors.
	Return DataToSave object containing formatted LiDAR data.
	*/
	DataToSave tempData; // Temporary data point from scan.
	// std::vector<DataToSave> tempVector;  // Temporary vector to store all data from scan.
	rplidar_response_measurement_node_hq_t nodes[512]; // Create response node of size 512.
	size_t count = _countof(nodes);

	op_result = driver->grabScanDataHq(nodes, count); // Hq method coincides with rplidar_..._node_hq_t.

	if (IS_FAIL(op_result))
	{
		printf("Failed to get scan data.");
		tempData.invalid_data = true;
		return tempData;
	}
	else
	{
		for (int pos = 0; pos < (int)count; ++pos)
		{
			tempData.theta_deg.push_back(nodes[pos].angle_z_q14 * 90.f / (1 << 14));
			tempData.distance_mm.push_back(nodes[pos].dist_mm_q2 / (1 << 2));
		}
		return tempData;
	}
}

std::vector<float> scale_vector(std::vector<float> v, int max_val)
{
	/*
	Perform min/max scaling on entire vector.
	Parameters:
	 	v - Vector containing unscaled float values.
		max_val - Maximum value for scale.
	*/
	std::vector<float> return_vector;
	for (uint i = 0; i < v.size(); i++)
	{
		float val = v[i];
		val = std::sqrt(std::sqrt(val)) / std::sqrt(std::sqrt(17000));
		val = val * max_val;
		return_vector.push_back(val);
	}

	return return_vector;
}

float deg_to_rad(float deg)
{
	/* 
	Convert measurement from degrees into radians. 
	Parameters:
		deg - A measurement of degrees, stored in float type.

	Returns:
		Radian value after conversion from degrees, as type float.
	*/
	return (deg *3.141592653589793) / 180.0;  // Convert degrees to radians.
}


cv::Mat get_model_input(const int img_size=32)
{
	/*
	Retrieves scan from LiDAR.
	Plots scan as 2D image used as input to prediction model.
	Returns:
		cv::Mat, an image of size (32, 32, 1) containing scan points.
	*/
	int img_center = img_size / 2;
	cv::Mat image;  // Initialize image container.
	image = cv::Mat::zeros(img_size, img_size, CV_8U);  // Resize container to 32x32x1, fill with 0s.
	DataToSave scan = get_lidar_data();  // Get latest scan from LiDAR.
	// Initialize two vectors, one for Xs, another for Ys.
	std::vector<float> scaled_dists = scale_vector(scan.distance_mm, img_center - 1);
	std::vector<int> x_points;
	std::vector<int> y_points;
	for (uint i = 0; i < scan.theta_deg.size(); i++)  // Loop over scan.
	{
		// Fill x-y-vectors with points calculated from scan.
		float theta_rad = deg_to_rad(scan.theta_deg[i]);
		x_points.push_back(std::round(scaled_dists[i] * std::sin(theta_rad)));
		y_points.push_back(std::round(scaled_dists[i] * std::cos(theta_rad)));
	}
	// Scale x-y-vectors as to fit in image container.
	// std::vector<int> scaled_x_pts = scale_vector(x_points, img_center - 1);
	// std::vector<int> scaled_y_pts = scale_vector(y_points, img_center - 1);

	for (uint i = 0; i < x_points.size(); i++)  // Loop over scaled x-y-vectors.
	{
		// Fill in image with points, accounting for origin at center.
		int x_index = x_points[i] + img_center;
		int y_index = img_center - y_points[i];
		image.at<uchar>(y_index, x_index) = 255;
	}
	// cv::imwrite("ScanImg.jpeg", image);

	return image;
} 

void setup_camera(const int h = 64, const int w = 64)
{
	// cap.open("/dev/video0");  // Open camera for reading.
	cap.set(cv::CAP_PROP_FRAME_HEIGHT, h);
	cap.set(cv::CAP_PROP_FRAME_WIDTH, w);
}

cv::Mat get_current_frame()
{
	cv::Mat frame;
	cv::Mat gray;

	if (!cap.isOpened())
		std::cout << "\nCould not open camera.\n";

	cap.read(frame);
	// cap >> frame;

	if (frame.empty())
	{
		std::cout << "Empty frame in get_current_frame!";
	}
	cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY); 

	return gray;
}


void assign_virtual_joystick(float x, float y)
{
	/*
	Assigns global virtual joystick values calculated from steering angle.
	Parameters:
		steer_angle_deg - A float type containing angle in range [-90, 90].
	*/
	DRIVE_INSTR.virt_joystick_x = x * 127;
	DRIVE_INSTR.virt_joystick_y = y * 127;
}

// void assign_virtual_joystick(int8_t x, int8_t y)
// {
// 	DRIVE_INSTR.virt_joystick_x = x;
// 	DRIVE_INSTR.virt_joystick_y = y;
// 	// std::cout << "X: " << int(x) << "\tY: " << int(y) << "\n";
// }

int8_t from_categorical(int idx, int num_classes)
{
	return ((((idx * 2) / (num_classes - 1)) - 1) * 127);
}


int main(int argc, const char *argv[])
{
	connect_i2c();
	signal(SIGINT, ctrlc);
	// Debugging OpenCV linking issues. Should be version 4.3.0.
	printf("opencv version: %d.%d.%d\n",CV_VERSION_MAJOR,CV_VERSION_MINOR,CV_VERSION_REVISION);
	// Load keras model using frugally-deep.
	const auto model = fdeep::load_model("/home/linaro/Documents/Rowbot/rplidar/sdk/app/ultra_simple/export_model.json");
	int counter = 0;

	while (true)
	{
		MCU_PACKAGE = rdwr_buffer(DRIVE_INSTR); // Read/write data from/to arduino.

		if (MCU_PACKAGE.Shutdown)
		{
			printf("Shutdown Initiated.");
			if (CSV_FILE.is_open())
			{
				CSV_FILE << "\nShutdown Initiated While Saving Scan Data";
				CSV_FILE.close();
			}
			system("sudo shutdown now");
		}

		if (MCU_PACKAGE.DriveAutonomously)
		{
			if (!PREV_AUTO_STATE) // Need to setup for auto driving.
			{
				counter = 0;
				PREV_AUTO_STATE = true;
				setup_lidar();
				setup_camera(64, 64);  // Setup camera with parameters `height, width`.
				printf("\nAutonomous Driving Initiated.\n");
			}
			counter += 1;
			// Get scan as 2D image, run image through prediction model.
			cv::Mat scan_image = get_model_input(64);
			if (counter == 45)
				cv::imwrite("/home/linaro/Documents/Rowbot/rplidar/sdk/output/Linux/Release/ScanImg.png", scan_image);

			const auto input = fdeep::tensor_from_bytes(scan_image.ptr(),
	        	static_cast<std::size_t>(scan_image.rows),
	        	static_cast<std::size_t>(scan_image.cols),
	        	static_cast<std::size_t>(scan_image.channels()),
	        	0.0f, 1.0f);

	    	const auto result = model.predict({input});
			// std::cout << fdeep::show_tensors(result) << std::endl;
			const auto x_y_joystick = *result[0].as_vector();
			// Send drive instructions based on steering prediction.
			assign_virtual_joystick(x_y_joystick[0], x_y_joystick[1]);

			/* Below was used for a categorical prediction model. */
			// const auto x_vector = *result[0].as_vector();
			// const auto y_vector = *result[1].as_vector();

			// const int max_x_idx = std::distance(x_vector.begin(),std::max_element(x_vector.begin(), x_vector.end()));
			// const int max_y_idx = std::distance(y_vector.begin(),std::max_element(y_vector.begin(), y_vector.end()));
			
			// // std::cout << "Size of vector: " << x_vector.size() << "\n";

			// assign_virtual_joystick(
			// 	from_categorical(max_x_idx, x_vector.size()),
			// 	from_categorical(max_y_idx, y_vector.size())
			// 	);

			// Printing index of max values.
			// std::cout << "Max X: ";
			// std::cout << std::distance(x_vector.begin(),std::max_element(x_vector.begin(), x_vector.end())) << "\n";
			// std::cout << "Max Y: ";
			// std::cout << std::distance(x_vector.begin(),std::max_element(x_vector.begin(), x_vector.end())) << "\n";
		}
		else if (PREV_AUTO_STATE) // Switched autonomous driving off.
		{
			printf("Turning Off Autonomous Driving.\n");
			DRIVE_INSTR.virt_joystick_x = 0;
			DRIVE_INSTR.virt_joystick_y = 0;
			shutdown_lidar();
			PREV_AUTO_STATE = false;
		}

		if (MCU_PACKAGE.SaveScanData)
		{
			// int scan_counter;
			if (!PREV_SAVE_STATE) // Setup for saving lidar data.
			{
				printf("Data Save Initiated.");
				// scan_counter = 0;
				PREV_SAVE_STATE = true;
				setup_lidar();
				setup_camera(64, 64);  // Setup camera with parameters `height, width`.
				CSV_FILE.open("/home/linaro/Documents/Rowbot/rplidar/sdk/output/Linux/Release/SaveScanTest.csv", std::ios::app);
			}
			DataToSave scan = get_lidar_data();
			cv::Mat img = get_current_frame();

			if (img.empty())
			{
				std::cout << "Empty frame in main!";
				img = cv::Mat::zeros(64, 64, CV_8U);
			}

			// CSV_FILE << "Scan," << scan_counter << "\n";
			CSV_FILE << "Joystick X," << (int)MCU_PACKAGE.joystick_x << "\n";
			CSV_FILE << "Joystick Y," << (int)MCU_PACKAGE.joystick_y << "\n";
			CSV_FILE << "Theta";  // Following is the writing of each element in theta vector.
			for (uint i = 0; i < scan.theta_deg.size(); i++)
			{
				CSV_FILE << "," << scan.theta_deg[i];
			}
			CSV_FILE << "\n";  // End line for next entry.

			CSV_FILE << "Distance";  // Following is the writing of each element in the distance vector.
			for (uint i = 0; i < scan.distance_mm.size(); i++)
			{
				CSV_FILE << "," << scan.distance_mm[i];
			}
			CSV_FILE << "\n";
			
			CSV_FILE << "Image,";
			CSV_FILE << cv::format(img, cv::Formatter::FMT_CSV) << std::endl;

			// scan_counter += 1;  // Increment `scan_counter` to keep track of data.
		}
		else if (PREV_SAVE_STATE)
		{
			printf("Turning Off Data Save.\n");
			CSV_FILE.close();
			shutdown_lidar();
			PREV_SAVE_STATE = false;
		}

		if (ctrl_c_pressed)
		{
			shutdown_lidar();
			if (CSV_FILE.is_open())
			{
				CSV_FILE.close();
			}
			printf("Exiting Program.\n");
			return 0;
		}
	}
}