# user_interface_py_pkg
## Introduction
This package contains the implementation of an interactive user-interface within Python-3.10.20. This has been developed as part of the MSC Robotics Group Project 2025-2026 at Cranfield University. 

## Requirements
To execute this package, your Python environment must have a number of packages installed. If you have a version of miniforge (conda / mamba) installed, please use the environment.yaml file to create a new environment, it will save you time.

General Packages:
- ROS2 Humble (for rclpy)

Python Packages:
- numpy : Version <2
- HoloViews : Lastest version
- Panel : Latest version
- jupyter_bokeh : Latest version

## Execution
In order to execute, enter the following code below:
```
cd user_interface_py_pkg
python gui.py
```

Note, that for the full UI to run as intended, please see the repository ReadMe.md file for full execution. Without executing the launch files for the simulation and system_manager_py_pkg, data will be missing on the user interface.

## Additional Information
Author: Nathan Horder (nathan.horder.700@cranfield.ac.uk)
Developed as part of Cranfield University MSC Robotics Group Project 2025-2026