from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():

    default_path = './ORT_QR'

    return LaunchDescription([

        DeclareLaunchArgument(
            'path',
            default_value=default_path,
            description='Path to save the QR code data'
        ),


        # ----------------------------------------------------------------
        # QR CODE DATA EXTRACTION & SAVING
        # ----------------------------------------------------------------

        Node(
            package='wall_painting_robot',
            executable='feature_detection',
            parameters=[{
                "folder_path": LaunchConfiguration('path'),
            }]
        ),

        ExecuteProcess(
            cmd=[
                'xdg-open', LaunchConfiguration('path'),
            ],
            shell=False
        ),

        # ----------------------------------------------------------------
        # ROBOT STATUS MONITORING
        # ----------------------------------------------------------------
        ExecuteProcess(
            cmd=[
                'gnome-terminal', '--',
                'ros2', 'run', 'wall_painting_robot', 'robot_monitor'
            ],
            shell=False
        )
    ])
     




