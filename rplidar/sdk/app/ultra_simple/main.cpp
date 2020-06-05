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
	rplidar_response_measurement_node_hq_t nodes[256]; // Create response node of size 256.
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

std::vector<int> scale_vector(std::vector<float> v, int min_val, int max_val)
{
	/*
	Perform min/max scaling on entire vector.
	Parameters:
	 	v - Vector containing unscaled float values.
	 	min_val - Minimum value for scale.
		max_val - Maximum value for scale.
	*/
	std::vector<int> return_vector;
	float min = *std::min_element(v.begin(), v.end());  // Get smallest element.
	float max = *std::max_element(v.begin(), v.end());  // Get largest element.
	for (uint i = 0; i < v.size(); i++)  // Loop over vector.
	{
		// Append scaled value to `return_vector`.
		return_vector.push_back(int(((v[i] - min)/(max - min)) * (max_val - min_val)) + min_val);
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


cv::Mat get_model_input()
{
	/*
	Retrieves scan from LiDAR.
	Plots scan as 2D image used as input to prediction model.
	Returns:
		cv::Mat, an image of size (32, 32, 1) containing scan points.
	*/
	cv::Mat image;  // Initialize image container.
	image = cv::Mat::zeros(32, 32, CV_8U);  // Resize container to 32x32x8, fill with 0s.
	DataToSave scan = get_lidar_data();  // Get latest scan from LiDAR.
	// Initialize two vectors, one for Xs, another for Ys.
	std::vector<float> x_points;
	std::vector<float> y_points;
	for (uint i = 0; i < scan.theta_deg.size(); i++)  // Loop over scan.
	{
		// Fill x-y-vectors with points calculated from scan.
		float theta_rad = deg_to_rad(scan.theta_deg[i]);
		x_points.push_back(std::round(scan.distance_mm[i] * std::sin(theta_rad)));
		y_points.push_back(std::round(scan.distance_mm[i] * std::cos(theta_rad)));
	}
	// Scale x-y-vectors as to fit in image container.
	std::vector<int> scaled_x_pts = scale_vector(x_points, 0, 31);
	std::vector<int> scaled_y_pts = scale_vector(y_points, 0, 31);

	for (uint i = 0; i < scaled_x_pts.size(); i++)  // Loop over scaled x-y-vectors.
	{
		// Fill in image with points. 
		image.at<uchar>(scaled_x_pts[i], scaled_y_pts[i]) = 255;
	}

	return image;
} 


void assign_virtual_joystick(float steer_angle_deg)
{
	/*
	Assigns global virtual joystick values calculated from steering angle.
	Parameters:
		steer_angle_deg - A float type containing angle in range [-90, 90].
	*/
	DRIVE_INSTR.virt_joystick_x = 127 * std::sin(deg_to_rad(steer_angle_deg));
	DRIVE_INSTR.virt_joystick_y = 127 * std::cos(deg_to_rad(steer_angle_deg));
	// Debugging drive instructions.
	// std::cout << "VJYX: " << int(DRIVE_INSTR.virt_joystick_x);
	// std::cout << "\tVJYY: " << int(DRIVE_INSTR.virt_joystick_y) << "\n";
}


int main(int argc, const char *argv[])
{
	connect_i2c();
	signal(SIGINT, ctrlc);
	// Debugging OpenCV linking issues. Should be version 4.3.0.
	printf("opencv version: %d.%d.%d\n",CV_VERSION_MAJOR,CV_VERSION_MINOR,CV_VERSION_REVISION);
	// Load keras model using frugally-deep.
	const auto model = fdeep::load_model("/home/linaro/Documents/Rowbot/rplidar/sdk/app/ultra_simple/export_model.json");

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
				PREV_AUTO_STATE = true;
				setup_lidar();
				printf("\nAutonomous Driving Initiated.\n");
			}
			// Get scan as 2D image, run image through prediction model.
			cv::Mat image = get_model_input();
			const auto input = fdeep::tensor_from_bytes(image.ptr(),
	        	static_cast<std::size_t>(image.rows),
	        	static_cast<std::size_t>(image.cols),
	        	static_cast<std::size_t>(image.channels()),
	        	0.0f, 1.0f);

	    	const auto result = model.predict_single_output({input});
			float steering_angle = result * 90;
			assign_virtual_joystick(steering_angle);
		}
		else if (PREV_AUTO_STATE) // Switched autonomous driving off.
		{
			printf("Turning Off Autonomous Driving.\n");
			shutdown_lidar();
			PREV_AUTO_STATE = false;
		}

		if (MCU_PACKAGE.SaveScanData)
		{
			int scan_counter;
			if (!PREV_SAVE_STATE) // Setup for saving lidar data.
			{
				printf("Data Save Initiated.");
				scan_counter = 0;
				PREV_SAVE_STATE = true;
				setup_lidar();
				CSV_FILE.open("SaveScanTest.csv");
			}
			DataToSave scan = get_lidar_data();

			CSV_FILE << "Scan," << scan_counter << "\n";
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

			scan_counter += 1;  // Increment `scan_counter` to keep track of data.
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