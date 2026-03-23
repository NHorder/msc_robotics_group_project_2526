#!/usr/bin/env python3
"""
Launch ORB-SLAM3 mono_imu with configuration for Gazebo simulation
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    
    return LaunchDescription([

        # ORB-SLAM3 Mono node (without IMU)
        Node(
            package='orb_slam3_ros',
            executable='orb_slam3_ros_mono',
            output='screen',
            parameters=[{
                'settings_file': PathJoinSubstitution([FindPackageShare('wall_painting_robot'), 'config', 'vslam_robot_config.yaml']),
                'world_frame_id': 'map',
                'show_viewer': False
            }],
            remappings=[
                ('/image_raw', '/camera/image_raw'),  # Camera topic
            ],
        )
])
