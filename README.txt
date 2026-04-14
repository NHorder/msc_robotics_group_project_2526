# Requirements
Ubuntu-22.04
ROS2 Humble

Packages:
- ros-humble-slam-toolbox

# Execution Steps:
1) cd ~/gdp_simulation
2) colcon build
3) source install/setup.bash
4) ros2 launch wall_painting_robot simulation.launch.py

5) In New Terminal: Launch SLAM toolbox
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true slam_params_file:=/home/ubuntu2204/gdp_simulation/src/wall_painting_robot/config/slam_toolbox.yaml

6) In New Terminal: 
rviz2

Add to RVIZ2:
- Fixed Frame = map
- TF
- LaserScan topic: /scan
- Map topic: /map
