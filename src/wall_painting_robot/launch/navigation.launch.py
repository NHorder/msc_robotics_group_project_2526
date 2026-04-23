import os
from launch import LaunchDescription
from launch.actions import (IncludeLaunchDescription, ExecuteProcess, TimerAction)
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg      = FindPackageShare('wall_painting_robot').find('wall_painting_robot')
    nav2_pkg = FindPackageShare('nav2_bringup').find('nav2_bringup')
    map_file = os.path.join(os.path.expanduser('~'), 'room_map.yaml')

    return LaunchDescription([

        # 1. Simulation (Gazebo + bridge + robot spawn)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg, 'launch', 'simulation.launch.py'))),

        # 2. Wall detector
        Node(package='wall_painting_robot', executable='wall_detector',
             name='wall_detector', output='screen',
             parameters=[{'use_sim_time': True}]),

        # 3. Odom to TF
        Node(package='wall_painting_robot', executable='odom_to_tf',
             name='odom_to_tf', output='screen'),

        # 4. Nav2 — delayed 20s for Gazebo + TF to fully init
        TimerAction(period=20.0, actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(nav2_pkg, 'launch', 'bringup_launch.py')),
                launch_arguments={
                    'map':          map_file,
                    'use_sim_time': 'true',
                    'params_file':  os.path.join(pkg, 'config', 'nav2_params.yaml'),
                    'autostart':    'True',
                }.items())]),

        # 4b. Manually activate bt_navigator after 35s (workaround for sim time race)
        TimerAction(period=35.0, actions=[
            ExecuteProcess(
                cmd=['bash', '-c',
                     'source /opt/ros/humble/setup.bash && '
                     'ros2 lifecycle set /bt_navigator activate || true'],
                output='screen')]),

        # 5. RViz — delayed 12s
        TimerAction(period=12.0, actions=[
            Node(package='rviz2', executable='rviz2', name='rviz2',
                 output='screen',
                 arguments=['-d', os.path.join(pkg, 'config', 'navigation.rviz')])]),

        # 6. Send arm to upright position (all joints=0) — delayed 8s
        TimerAction(period=8.0, actions=[
            ExecuteProcess(
                cmd=['bash', '-c',
                     'source /opt/ros/humble/setup.bash && '
                     'source ~/gdp_simulation/install/setup.bash && '
                     'ros2 topic pub -r 10 /model/wall_painting_robot/joint1/cmd_pos '
                     'std_msgs/msg/Float64 "{data: 0.0}" & '
                     'ros2 topic pub -r 10 /model/wall_painting_robot/joint2/cmd_pos '
                     'std_msgs/msg/Float64 "{data: 0.30}" & '
                     'ros2 topic pub -r 10 /model/wall_painting_robot/joint3/cmd_pos '
                     'std_msgs/msg/Float64 "{data: -2.55}" & '
                     'ros2 topic pub -r 10 /model/wall_painting_robot/joint4/cmd_pos '
                     'std_msgs/msg/Float64 "{data: 1.0}" & '
                     'ros2 topic pub -r 10 /model/wall_painting_robot/joint5/cmd_pos '
                     'std_msgs/msg/Float64 "{data: 0.0}" & '
                     'sleep 5 && kill $(jobs -p)'],
                output='screen')]),

        # 7. Wall selector xterm — delayed 40s (after Nav2 fully active)
        TimerAction(period=10.0, actions=[
            ExecuteProcess(
                cmd=['xterm', '-title', 'Wall Selector',
                     '-fa', 'Monospace', '-fs', '13',
                     '-bg', 'black', '-fg', 'white',
                     '-geometry', '75x38+50+50',
                     '-e', 'bash', '-c',
                     'source /opt/ros/humble/setup.bash && '
                     'source ~/gdp_simulation/install/setup.bash && '
                     'echo "Step 1: ros2 service call /detect_walls std_srvs/srv/Trigger {}" && '
                     'echo "Step 2: Select wall A/B/C/D" && '
                     'echo "Step 3: Once arrived, open NEW terminal:" && '
                     'echo "  ros2 launch wall_painting_robot painting.launch.py wall_key:=B" && '
                     'echo "" && '
                     'ros2 run wall_painting_robot wall_selector; '
                     'echo "Exited. Press Enter."; read'],
                output='screen')]),
    ])
