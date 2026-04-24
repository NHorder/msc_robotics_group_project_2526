import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    pkg_path = FindPackageShare('wall_painting_robot').find('wall_painting_robot')

    return LaunchDescription([

        # --------------------------------------------------
        # 1. Gazebo + robot + bridges
        # --------------------------------------------------
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_path, 'launch', 'gazebo.launch.py')
            ),
        ),

        # --------------------------------------------------
        # 2. Teleoperation
        # --------------------------------------------------
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_path, 'launch', 'gcs_teleop.launch.py')
            ),
        ),

    ])
