# msc_robotics_group_project_2526
# Introduction
MSC Robotics Group Project 2025-2026.  

Title: Mobile Manipulators in Housing Construction  


Main documents will be shared on teams (A folder may be present here at a later date)  


# Contribution Guidlines
- Never push to main
- Work on branches
- Clean up mistake commits before submission
- Work with application lead if conflicts arise

# Installation Guide
Ubuntu-22.04

ROS2 Humble

Python-3.10.20


ROS2 packages can be installed using the command: sudo apt install 


ROS2 Packages:

- ros-humble-slam-toolbox
- ros-humble-ros-gz

Python packages can be installed using: pip install

If miniforge or conda-forge (Package handlers) is already installed, create an environment using visnat_conda_env.yaml, then activate it. 

Miniforge installation and activation: https://github.com/conda-forge/miniforge 

Python Packages:
- 


## System Execution

In order to execute the entire system, please follow the steps provided below, please replace gdp_simulation with your respective filename.

1) Open five terminals (and connect to Ubuntu if applicable, `wsl -d Ubuntu-22.04`)
2) `cd ~/gdp_simulation` (all terminals)
3) `colcon build` (first terminal)
4) `source install/setup.bash` (all terminals)

ROS2 Nodes:

5) In Terminal 1: Launch ROS2 nodes: `ros2 launch system_manager_py_pkg system_launch.py`

Simulation:

6) In Terminal 2: Launch simulation: `ros2 launch wall_painting_robot simulation.launch.py (Terminal 2)`
7) In Terminal 3: Launch SLAM toolbox: `ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true slam_params_file:=./src/wall_painting_robot/config/slam_toolbox.yaml`
8) In Terminal 4: Load RVIZ2:  `rviz2`
9) In Terminal 4: Add to RVIZ2:
    - Fixed Frame = map
    - TF
    - LaserScan topic: /scan
    - Map topic: /map

User Interface:

10) In Terminal 5: Navigate to UI package: cd user_interface_py_pkg/user_interface_py_pkg
11) In Terminal 5: Ensure required packages are installed, or conda environment is created using environment.yaml (`conda create -f environment.yaml` (You can include `-n my_env_name` for custom environment name))
12) In Terminal 5: Serve the UI: `python gui.py`
13) In Terminal 5: Load the UI in a browser: Copy-paste the printed URL into browser

NOTE: If execution of step 6 fails, presenting an OGRE error within the output, run the commands below to force Gazebo to run using the CPU instead of the GPU:

```
export IGN_RENDERING_ENGINE=ogre 
export LIBGL_ALWAYS_SOFTWARE=1
export MESA_LOADER_DRIVER_OVERRIDE=llvmpipe
```

The OGRE error relates to the execution of the simulation using the GPU, hence forcing it run to CPU may solve the problem.

# Who is involved:
Developers / Students: Sébastien Dubois, Alma Toleubekova, Nathan Horder, Tanish Ganesh Dahiwal and Viksit Sachdeva.

Academic Supervisors: Dr Gilbert Tang and Prof Phill Webb.

# Additional Comments / Notes

System Safety: A package that is not included as part of the system execution due to missing Entity identification class. Used to present a possible method for ensuring system safety

# ROS2 Topics

## Sensor Topics
Camera:

/camera/compressedDepth

/camera/image_raw

/camera/image_raw/compressed

/camera/theora

/camera_info



LiDAR:

/scan

/processed/scan


## Motion
/imu

/wheel_odom

/join_states

/joy

/joy/set_feedback

/led

## Motion Planning

## User Interface
/gui/action

/system_health

/wall/designation

/wall/recalculate


## Misc
/safety

/clock

/parameter_events

/robot_description

/rosout

/take_picture

/tf

/tf_static