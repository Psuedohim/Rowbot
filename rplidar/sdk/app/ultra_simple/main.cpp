#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <iostream>
#include <fstream>
#include "i2c_comm.h"
#include "rplidar.h" //RPLIDAR standard sdk, all-in-one header
// #include "radio_control.h"  // Arduino is currently handling RC.

using namespace rp::standalone::rplidar;

RPlidarDriver *driver; // Initialize pointer for LiDAR driver.
u_result op_result;

#ifndef _countof
#define _countof(_Array) (int)(sizeof(_Array) / sizeof(_Array[0]))
#endif

bool ctrl_c_pressed;
bool PREV_AUTO_STATE;
bool PREV_SAVE_STATE;
I2C_IN_PACK MCU_PACKAGE;
I2C_OUT_PACK DRIVE_INSTR;

std::ofstream CSV_FILE; // For saving scan data.

struct DataToSave
{
	std::vector<float> theta_deg;
	std::vector<float> distance_mm;
	int8_t joystick_x;
	int8_t joystick_y;
}

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
}

void shutdown_lidar()
{
	driver->stop();			 // Stop scanning.
	driver->stopMotor(); // Stop spinning RPLiDAR motor.
}

DataToSave get_lidar_data()
{
	DataToSave tempData; // Temporary data point from scan.
	// std::vector<DataToSave> tempVector;  // Temporary vector to store all data from scan.
	rplidar_response_measurement_node_hq_t nodes[512]; // Create response node
	size_t count = _countof(nodes);

	op_result = driver->grabScanDataHq(nodes, count); // Hq method coincides with rplidar_..._node_hq_t.

	if (IS_FAIL(op_result))
	{
		printf("Failed to get scan data.");
		return false;
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

int main(int argc, const char *argv[])
{
	signal(SIGINT, ctrlc);
	MCU_PACKAGE = rdrw_buffer(); // Read/write data from/to arduino.

	if (MCU_PACKAGE.Shutdown)
	{
		if (CSV_FILE.is_open())
		{
			CSV_FILE << "\nShutdown Initiated While Saving Scan Data";
			CSV_FILE.close();
		}
		system("sudo shutdown now")
	}

	if (MCU_PACKAGE.DriveAutonomously)
	{
		if (!PREV_AUTO_STATE) // Need to setup for auto driving.
		{
			PREV_AUTO_STATE = true;
			setup_lidar();
		}
		DataToSave scan = get_lidar_data();
		// To Do: Use `scan` to navigate based on model predictions.
	}
	else if (PREV_AUTO_STATE) // Switched autonomous driving off.
	{
		PREV_AUTO_STATE = false;
		shutdown_lidar();
	}
}

	if (MCU_PACKAGE.SaveScanData)
	{
		if (!PREV_SAVE_STATE) // Setup for saving lidar data.
		{
			int scan_counter = 0;
			PREV_SAVE_STATE = true;
			setup_lidar();
			CSV_FILE.open("SaveScanTest.csv");
		}
		DataToSave scan = get_lidar_data();
		CSV_FILE << "Scan No. " << scan_counter << "\n";
		CSV_FILE << "Theta, Distance, Joystick X, Joystick Y\n";
		for (int i = 0; i < lidar_scan.theta_deg.size(); i++)
		{
			CSV_FILE << scan.theta_deg[i] << ", ";
			CSV_FILE << scan.distance_mm[i] << ", ";
			CSV_FILE << MCU_PACKAGE.joystick_x << ", ";
			CSV_FILE << MCU_PACKAGE.joystick_y << "\n";
		}
	}
	else if (PREV_SAVE_STATE)
	{
		CSV_FILE.close();
		shutdown_lidar();
	}
}
else if (PREV_SAVE_STATE)
{
	CSV_FILE.close();
	shutdown_lidar();
}
}
