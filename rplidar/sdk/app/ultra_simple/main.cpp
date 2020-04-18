#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <iostream>
// #include <unistd.h>				//Needed for I2C port
// #include <fcntl.h>				//Needed for I2C port
// #include <sys/ioctl.h>			//Needed for I2C port
// #include <linux/i2c-dev.h>		//Needed for I2C port
#include "i2c_comm.h"


#include "rplidar.h" //RPLIDAR standard sdk, all-in-one header
// #include "i2c_comm.h"

using namespace rp::standalone::rplidar;

RPlidarDriver * driver;
u_result     op_result;

#ifndef _countof
#define _countof(_Array) (int)(sizeof(_Array) / sizeof(_Array[0]))
#endif

bool ctrl_c_pressed;

int file_i2c;
int length = 3;  //<<< Number of bytes to write
int addr = 0x04;  //<<<<<The I2C address of the slave.
unsigned char * buffer[3] = {0};
char *filename = (char*)"/dev/i2c-7";

// void write_to_i2c()
// {
// 	printf("Got to method!\n");

// 	// buffer[1] = 0x03;
// 	// buffer[2] = 0x07;
// 	if ((file_i2c = open(filename, O_RDWR)) < 0)
// 	{
// 		printf("Error No. %d", file_i2c);
// 		//ERROR HANDLING: you can check errno to see what went wrong.
// 		printf("Failed to open the i2c bus");
// 		// return false;
// 	}
	
// 	if (ioctl(file_i2c, I2C_SLAVE, addr) < 0)
// 	{
// 		printf("Failed to acquire bus access and/or talk to slave.\n");
// 		// return false;
// 	}
// 	//write() returns the number of bytes actually written, if it doesn't match then an error occurred (e.g. no response from the device)
// 	if (write(file_i2c, buffer, length) != length)  
// 	{
// 		/* ERROR HANDLING: i2c transaction failed */
// 		printf("Failed to write to the i2c bus.\n");
// 		// return false;
// 	}

// 	// return true;
// }


void ctrlc(int)
{
	ctrl_c_pressed = true;
}

bool checkRPLIDARHealth(RPlidarDriver* driver)
{
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
	const char* opt_com_path = NULL;
	opt_com_path = "/dev/ttyUSB0";

	// create the driver instance
	driver = RPlidarDriver::CreateDriver(DRIVER_TYPE_SERIALPORT);
	if (!driver) {
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
		// goto on_finished;
	 	RPlidarDriver::DisposeDriver(driver);
	 	driver = NULL;
	}

	// on_finished:
	// 	RPlidarDriver::DisposeDriver(driver);
	// 	driver = NULL;
}


// tuple<double, double> get_measurement()
// {

// }

int main(int argc, const char* argv[]) 
{

	printf("Got here");
	// while (true)
	// {
	// 	// write_to_i2c();
	// 	printf("Sending Data\n");
	// 	write_buffer(0, 1);
	// }

	setup_lidar();
	signal(SIGINT, ctrlc);

	printf("Got Here");
	driver->startMotor();
	// Start scan.
	RplidarScanMode scanMode;
	driver -> startScan(false, true, 0, &scanMode);
	//driver->startScan(0, 1);

	// fetch result and print it out...
	while (true) {
		rplidar_response_measurement_node_hq_t nodes[8192];  // Supposed to be better.
		size_t   count = _countof(nodes);

		op_result = driver->grabScanDataHq(nodes, count);  // Hq method coincides with rplidar_..._node_hq_t.
		

		for (int pos = 0; pos < (int)count; ++pos) 
		{
			
			float angle = nodes[pos].angle_z_q14 * 90.f / (1 << 14);
			float distance = nodes[pos].dist_mm_q2 / (1 << 2);

			if ((int)angle > 345 || (int)angle < 15)
			{
				printf("theta: %03.2f Dist: %08.2f\n", angle, distance);
				if (distance > 300)
				{
					write_buffer(0, 1);
				}
				else
				{
					write_buffer(0, 0);
				}

			}

		}

		// printf("Sending Data\n");
		// write_buffer(0, 1);

		if (ctrl_c_pressed) {
			break;
		}
	}

	write_buffer(0, 0);
	driver->stop();
	driver->stopMotor();


}