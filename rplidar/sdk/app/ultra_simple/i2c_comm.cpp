#include "i2c_comm.h"


bool write_buffer(int8_t theta, int8_t drive)
{
	char *filename = (char*)"/dev/i2c-7";  // MCU connected to I2C bus number 7.
	int file_i2c;
	int length = 3;  // Number of bytes to write to MCU.
	int addr = 0x04;  // The I2C address of the MCU.
	int8_t buffer[3];  // Initialize buffer to write to MCU over I2C.
	buffer[0] = 0;  // Starting Bit.
	buffer[1] = theta;  // Theta instruction.
	buffer[2] = drive;  // Drive instruction.

	if ((file_i2c = open(filename, O_RDWR)) < 0)
	{
		printf("Error No. %d", file_i2c);
		//ERROR HANDLING: you can check errno to see what went wrong.
		printf("Failed to open the i2c bus");
		return false;
	}
	
	if (ioctl(file_i2c, I2C_SLAVE, addr) < 0)
	{
		printf("Failed to acquire bus access and/or talk to slave.\n");
		return false;
	}
	//write() returns the number of bytes actually written, if it doesn't match then an error occurred (e.g. no response from the device)
	if (write(file_i2c, buffer, length) != length)  
	{
		/* ERROR HANDLING: i2c transaction failed */
		printf("Failed to write to the i2c bus.\n");
		return false;
	}

	return true;
}
