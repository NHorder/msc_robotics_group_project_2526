from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='sensor_processing',
            executable='lidar_process',
            name='lidar_process',
            output='screen',
        ),
        Node(
            package='system_manager',
            executable='health',
            name='health',
            output='screen',
        ),
    ])