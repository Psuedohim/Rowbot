# What is a *Rowbot*?
*Rowbot* is an autonomous tractor, designed specifically for orchards. 

## What makes it autonomous?
Autonomy is accomplished by equipping the rover with cameras that can be used
for computer vision. The cameras will be used to identify a hose that runs
along the base of all the trees in a row. Data about the location of the hose,
relative to the center of the frame, will be used to inform the program on
which direction to turn towards.

Various sensors will be used to make the rover safe. These sensors include,
but are not limited to 
ultrasonic, lidar, infrared, temperature, humidity, gyroscopic,
and acceleration sensors. These sensors add to the shortcomings of computer 
vision. Computer vision is good at finding very specific objects but fails
at detecting potential hazards such as trees, vehicles, animals, or people.
This shortcoming requires the rover to be equipped with sensors that can 
detect a broad range of potential hazards. 



### Structure and Style
Creating an autonomous rover, especially one which maneuvers using computer
vision, is a big project. Breaking down the pieces of that project into
modular components not only helps this one project, but all future projects
that are in need of a similar guiding system. 
This project should be viewed as a set of tools for future versions of Rowbot.
All code should be broken apart into many methods. The reason for
this is to ensure bits and pieces of this program can be used as a set of tools
in the future. The breaking up of large methods is useful for debugging as 
issues can be traced back to individual methods as opposed to a whole page of 
code. 

A goal for the overall style of this project should be to keep code clean
and simple. This will make code re-working in the future much easier and 
enjoyable.

## Naming Conventions
Folder names should follow the camelCase naming convention. (arduinoPrograms)

File names should be all lowercase, words separated by underscores.
(motor_settings.ino)


### Dependencies
[opencv-python](https://github.com/skvark/opencv-python) and 
[Numpy](https://github.com/numpy/numpy) are dependencies for running the
the python programs included in this project.

## Outside Sources 
The following examples of using computer vision as a guidance system were used
to help in the creation of Rowbot.

- [OpenCV Lane Detection](https://github.com/galenballew/SDC-Lane-and-Vehicle-Detection-Tracking/tree/master/Part%20II%20-%20Adv%20Lane%20Detection%20and%20Road%20Features)

- [OpenCV Line Following Robot](https://einsteiniumstudios.com/beaglebone-opencv-line-following-robot.html)