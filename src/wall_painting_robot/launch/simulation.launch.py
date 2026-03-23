import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    pkg_path = FindPackageShare('wall_painting_robot').find('wall_painting_robot')

    return LaunchDescription([

        # Launch gazebo with map and bridge
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg_path, 'launch', 'gazebo.launch.py')),
        ),

        # Launch RViz with the simulation config
        # Node(
        #     package='rviz2',
        #     executable='rviz2',
        #     name='rviz',
        #     output='screen',
        #     arguments=['-d', os.path.join(FindPackageShare('wall_painting_robot').find('wall_painting_robot'), 'config', 'simulation.rviz')],
        #     respawn=False
        # )

        Node(
            package='wall_painting_robot',
            executable='qr_code_detection',
            name='qr_code_detection'
        ),

        # Launch teleoperation (keyboard and controller)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg_path, 'launch', 'gcs_teleop.launch.py')),
        ),

    ])
     




