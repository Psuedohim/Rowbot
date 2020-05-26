#include <unistd.h>        //Needed for I2C port
#include <fcntl.h>         //Needed for I2C port
#include <sys/ioctl.h>     //Needed for I2C port
#include <linux/i2c-dev.h> //Needed for I2C port
#include <stdio.h>
#include <stdlib.h>
#include <iostream>

struct I2C_IN_PACK;
struct I2C_OUT_PACK;

I2C_PACKAGE rdrw_buffer(I2C_PACKAGE);
