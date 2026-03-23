import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    pkg_path = FindPackageShare('wall_painting_robot').find('wall_painting_robot')

    return LaunchDescription([
        # Start webcam node with qr code detection
        Node(
            package='wall_painting_robot',
            executable='webcam',
            name='webcam',
            parameters=[{"enable_qr": True}],
        ),

        # Launch rqt_image_view to show the output
        Node(
            package='rqt_image_view',
            executable='rqt_image_view',
            name='qr_view',
            output='screen',
            arguments=['--ros-args',
                '-r', 'image:=/camera/detection_feed',
                '-p', 'image_transport:=compressed']
        )
    ])
     




