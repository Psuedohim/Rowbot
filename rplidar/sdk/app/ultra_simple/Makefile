#/*
# * Copyright (C) 2014  RoboPeak
# * Copyright (C) 2014 - 2018 Shanghai Slamtec Co., Ltd.
# *
# * This program is free software: you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program.  If not, see <http://www.gnu.org/licenses/>.
# *
# */
#
HOME_TREE := ../../

MODULE_NAME := $(notdir $(CURDIR))

include $(HOME_TREE)/mak_def.inc

CXXSRC += main.cpp
CXXSRC += i2c_comm.cpp
# CXXSRC += radio_control.cpp
C_INCLUDES += -I$(CURDIR)/../../sdk/include -I$(CURDIR)/../../sdk/src
C_INCLUDES += `pkg-config --cflags opencv4`

CFLAGS = -O  // I2C lib uses inline functions, suggested to add -O option.
# CFLAGS += `pkg-config --cflags opencv4`

# Include OpenCV compiled library.
LD_LIBS += `pkg-config --libs opencv4`


EXTRA_OBJ := 
LD_LIBS += -lstdc++ -lpthread -lm

all: build_app

include $(HOME_TREE)/mak_common.inc

clean: clean_app
