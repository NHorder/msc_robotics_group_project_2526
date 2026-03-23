first build:

cd ~/gdp_simulation
colcon build
source install/setup.bash
ros2 launch wall_painting_robot simulation.launch.py



in the new terminal launch slam toolbox:
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true slam_params_file:=/home/ubuntu2204/gdp_simulation/src/wall_painting_robot/config/slam_toolbox.yaml



new terminal:
rviz2




In RVIZ for mapping use:

Fixed Frame = map

add:
TF
LaserScan: topic /scan
Map: topic /map
