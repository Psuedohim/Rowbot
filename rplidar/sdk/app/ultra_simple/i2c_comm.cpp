#include "i2c_comm.h"

char *filename = (char *)"/dev/i2c-7"; // MCU connected to I2C bus number 7.
int addr = 0x04;											 // The I2C address of the MCU.
int file_i2c;

struct I2C_IN_PACK
{
	bool DriveAutonomously = false;
	// bool DriveByUser = false;
	bool SaveScanData = false;
	bool Shutdown = false;
	int8_t joystick_x = 0;
	int8_t joystick_y = 0;
}

struct I2C_OUT_PACK
{
	virt_joystick_x = 0;
	virt_joystick_y = 0;
}

bool
connect_i2c()
{
	if ((file_i2c = open(filename, O_RDWR)) < 0)
	{
		printf("Failed to open the i2c bus. Error No. %d\n", file_i2c);
		return false;
	}

	if (ioctl(file_i2c, I2C_SLAVE, addr) < 0)
	{
		printf("Failed to acquire bus access and/or talk to slave.\n");
		return false;
	}

	return true;
}

bool write_buffer(I2C_OUT_PACK buf_to_write)
{
	int length = sizeof(buf_to_write); // Number of bytes to write to MCU.
	if (!connect_i2c())								 // Connect to I2C bus.
		return false;

	//write() returns the number of bytes actually written, if it doesn't match then an error occurred (e.g. no response from the device)
	if (write(file_i2c, buffer, length) != length)
	{
		/* ERROR HANDLING: i2c transaction failed */
		printf("Failed to write to the i2c bus.\n");
		return false;
	}

	return true;
}

I2C_IN_PACK read_buffer()
{
	I2C_IN_PACK return_package;
	int size = sizeof(return_package);
	if (!connect_i2c()) // Connect to I2C bus.
		return false;

	if (read(file_i2c, return_package, size) != size)
	{
		/* ERROR HANDLING: i2c transaction failed */
		printf("I2C: Failure to read all bytes in structure.\n");
		return false;
	}

	return return_package;
}

I2C_IN_PACK rdrw_buffer(I2C_OUT_PACK buf_to_write)
{
	write_buffer(buf_to_write);
	I2C_IN_PACK return_data = read_buffer();
	if (return_data)
		return return_data;
}