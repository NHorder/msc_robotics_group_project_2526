from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import os

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='sensor_processing_py_pkg',
            executable='lidar'
        ),
        Node(
            package='system_manager_py_pkg',
            executable='health'
        ),
    ])