Project Structure and Documentation

All implementation files for this project are maintained within the project_01 directory of the GitHub repository.
Each source file includes appropriate header comments and in-line documentation describing its purpose, functionality, and usage, in accordance with the project requirements.

Software Build Instructions

Flash a Debian-based operating system image onto a microSD card for the PocketBeagle.

Boot the PocketBeagle and verify that it has a working internet connection.

Navigate to the project directory:

cd project_01


Install the required Python dependencies, including the IMU driver library:

pip3 install adafruit-circuitpython-bno055


Ensure that the PocketBeagle’s I²C interface is enabled prior to running the software, as it is required for communication with the BNO055 IMU.

Software Operation Instructions

Power the PocketBeagle and the external motor power supply.

Place the robot in an upright position on a level surface.

Execute the main control program:

python3 main.py


Carefully release the robot and observe its self-balancing behavior.

PID control gains may be adjusted within the software to improve stability and performance as needed.

Hackster.io Link

Additional project documentation, including images and a demonstration video, is available on Hackster.io:

https://www.hackster.io/joshua-aviles/self-balancing-robot

