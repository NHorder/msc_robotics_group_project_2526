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

# ROS 2 Topics

# Installation Guide

## Installation of software 

## Envrionment Setup
Ubuntu-22.04
ROS2 Humble

Packages:
- ros-humble-slam-toolbox
- ros-humble-ros-gz


### Simulation Execution
In order to run the simulation, please follow the steps provided below. Please replace gdp_simulation with 
your respective filename.

Note: For Step 5, if the local path does not work, please input a exchange the '.' to full path to src. Thank you.

1) cd ~/gdp_simulation
2) colcon build
3) source install/setup.bash
4) ros2 launch wall_painting_robot simulation.launch.py

5) In New Terminal: Launch SLAM toolbox
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true slam_params_file:=./src/wall_painting_robot/config/slam_toolbox.yaml

6) In New Terminal: 
rviz2

Add to RVIZ2:
- Fixed Frame = map
- TF
- LaserScan topic: /scan
- Map topic: /map

# Who is involved:
Developers / Students: Sébastien Dubois, Alma Toleubekova, Nathan Horder, Tanish Ganesh Dahiwal and Viksit Sachdeva.
Academic Supervisors: Dr Gilbert Tang and Prof Phill Webb.
