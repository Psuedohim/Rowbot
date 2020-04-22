#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <iostream>
#include "i2c_comm.h"
#include "rplidar.h" //RPLIDAR standard sdk, all-in-one header

using namespace rp::standalone::rplidar;

RPlidarDriver * driver;  // Initialize pointer for LiDAR driver.
u_result     op_result;

#ifndef _countof
#define _countof(_Array) (int)(sizeof(_Array) / sizeof(_Array[0]))
#endif

bool ctrl_c_pressed;


void ctrlc(int)
{
	/* This method is called when the user exits the program via `ctrl-c`.
	 * This will set a global variable, ctrl-c-pressed, to true, causing a 
	 * break in the control loop. 
	 */
	ctrl_c_pressed = true;
}


bool checkRPLIDARHealth(RPlidarDriver* driver)
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
		else {
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
	const char* opt_com_path = NULL;
	opt_com_path = "/dev/ttyUSB0";

	// Create the driver instance.
	driver = RPlidarDriver::CreateDriver(DRIVER_TYPE_SERIALPORT);
	if (!driver)  // If driver creation was not successful,
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
		fprintf(stderr, "Error, cannot bind to the specified serial port %s.\n"
			, opt_com_path);

	 	RPlidarDriver::DisposeDriver(driver);
	 	driver = NULL;
	}

	// print out the device serial number, firmware and hardware version number..
	printf("RPLIDAR S/N: ");
	for (int pos = 0; pos < 16; ++pos) {
		printf("%02X", devinfo.serialnum[pos]);
	}

	printf("\n"
		"Firmware Ver: %d.%02d\n"
		"Hardware Rev: %d\n"
		, devinfo.firmware_version >> 8
		, devinfo.firmware_version & 0xFF
		, (int)devinfo.hardware_version);

	// check health...
	if (!checkRPLIDARHealth(driver)) {
	 	RPlidarDriver::DisposeDriver(driver);
	 	driver = NULL;
	}
}


int main(int argc, const char* argv[]) 
{
	setup_lidar();
	signal(SIGINT, ctrlc);

	driver->startMotor();
	// Start scan.
	// RplidarScanMode scanMode;
	std::vector<RplidarScanMode> scanModes;
	driver->getAllSupportedScanModes(scanModes);
	// driver -> startScan(false, true, 0, &scanMode);
	driver->startScanExpress(false, scanModes[1].id);

	// fetch result and print it out...
	while (true) {
		rplidar_response_measurement_node_hq_t nodes[8192];  // Supposed to be better.
		// rplidar_response_measurement_node_hq_t nodes[1024];  // Supposed to be better.
		size_t   count = _countof(nodes);

		op_result = driver->grabScanDataHq(nodes, count);  // Hq method coincides with rplidar_..._node_hq_t.

		if (IS_FAIL(op_result))
			printf("Failed to get scan data.");

		for (int pos = 0; pos < (int)count; ++pos)
		{
			float angle = nodes[pos].angle_z_q14 * 90.f / (1 << 14);
			float distance = nodes[pos].dist_mm_q2 / (1 << 2);

			if ((int)angle > 355 || (int)angle < 5)
			{
				printf("theta: %03.2f Dist: %08.2f\n", angle, distance);
				if (distance > 800)
				{
					write_buffer(0, 1);
				}
				else
				{
					write_buffer(0, 0);
				}
			}
		}


		if (ctrl_c_pressed) {
			break;
		}
	}

	write_buffer(0, 0);  // Send stop signal to MCU.
	driver->stop();  // Stop scanning.
	driver->stopMotor();  // Stop spinning RPLiDAR motor.


}