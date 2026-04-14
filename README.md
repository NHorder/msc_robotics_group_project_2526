# msc_robotics_group_project_2526
# Introduction
MSC Robotics Group Project 2025-2026.\n
Title: Mobile Manipulators in Housing Construction\n\n

Main documents will be shared on teams (A folder may be present here at a later date)

# Contribution Guidlines
\t- Never push to main\n
\t- Work on branches\n
\t- Clean up mistake commits before submission\n
\t- Work with application lead if conflicts arise\n

# ROS2 Topics

## Sensor Topics
Camera:\n
/camera/compressedDepth\n
/camera/image_raw\n
/camera/image_raw/compressed\n
/camera/theora\n
/camera_info\n\n

LiDAR:\n
/scan\n
/processed/scan\n

## Motion
/imu\n
/wheel_odom\n
/join_states\n
/joy\n
/joy/set_feedback\n
/led\n

## Motion Planning

## User Interface
/gui/action\n
/system_health\n
/wall/designation\n
/wall/recalculate\n

## Misc
/safety\n
/clock\n
/parameter_events\n
/robot_description\n
/rosout\n
/take_picture\n
/tf\n
/tf_static\n

# Installation Guide
Ubuntu-22.04\n
ROS2 Humble\n
Python-3.10.20\n\n

ROS2 packages can be installed using the command: sudo apt install\n\n

ROS2 Packages:\n
\t- ros-humble-slam-toolbox\n
\t- ros-humble-ros-gz\n\n

Python packages can be installed using: pip install\n
If miniforge or conda-forge (Package handlers) is already installed, create an environment using visnat_conda_env.yaml, then activate it. \n
Miniforge installation and activation: https://github.com/conda-forge/miniforge \n\n

Python Packages:\n
\t- 
\n

## System Execution
In order to execute the entire system, please follow the steps provided below, please replace gdp_simulation with your respective filename.\n\n

1) Open five terminals (and connect to Ubuntu if applicable, `wsl -d Ubuntu-22.04`)\n
2) `cd ~/gdp_simulation` (all terminals)\n
3) `colcon build` (first terminal)\n
4) `source install/setup.bash` (all terminals)\n\n

ROS2 Nodes:\n
5) In Terminal 1: Launch ROS2 nodes: `ros2 launch system_manager_py_pkg system_launch.py`\n\n

Simulation:\n
6) In Terminal 2: Launch simulation: `ros2 launch wall_painting_robot simulation.launch.py (Terminal 2)`\n
7) In Terminal 3: Launch SLAM toolbox: `ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true slam_params_file:=./src/wall_painting_robot/config/slam_toolbox.yaml`\n
8) In Terminal 4: Load RVIZ2:  `rviz2`\n
9) In Terminal 4: Add to RVIZ2:\n
    \t- Fixed Frame = map\n
    \t- TF\n
    \t- LaserScan topic: /scan\n
    \t- Map topic: /map\n\n

User Interface:\n
10) In Terminal 5: Navigate to UI package: cd user_interface_py_pkg/user_interface_py_pkg\n
11) In Terminal 5: Ensure required packages are installed, or conda environment is created using environment.yaml (`conda create -f environment.yaml` (You can include `-n my_env_name` for custom environment name))\n
12) In Terminal 5: Serve the UI: `python gui.py`\n
13) In Terminal 5: Load the UI in a browser: Copy-paste the printed URL into browser\n\n

NOTE: If execution of step 6 fails, presenting an OGRE error within the output, run the commands below to force Gazebo to run using the CPU instead of the GPU:\n
```
export IGN_RENDERING_ENGINE=ogre 
export LIBGL_ALWAYS_SOFTWARE=1
export MESA_LOADER_DRIVER_OVERRIDE=llvmpipe
```\n
The OGRE error relates to the execution of the simulation using the GPU, hence forcing it run to CPU may solve the problem.\n

# Who is involved: 
Developers / Students: Sébastien Dubois, Alma Toleubekova, Nathan Horder, Tanish Ganesh Dahiwal and Viksit Sachdeva.\n
Academic Supervisors: Dr Gilbert Tang and Prof Phill Webb.\n

# Additional Comments / Notes
System Safety: A package that is not included as part of the system execution due to missing Entity identification class. Used to present a possible method for ensuring system safety\n