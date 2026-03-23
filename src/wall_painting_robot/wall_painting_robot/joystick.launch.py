import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    pkg_path = FindPackageShare('wall_painting_robot').find('wall_painting_robot')

    return LaunchDescription([

        # Launch joy node
        Node(
            package='joy',
            executable='joy_node'
        ),

        # Convert joy commands to cmd_vel Twist msg
        Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            parameters=[os.path.join(pkg_path,'config','joystick.yaml')]
        ),



        # Handling the buttons for still image and led toggle
        Node(
            package = 'wall_painting_robot',
            executable='joystick_commands',
            parameters=[os.path.join(pkg_path,'config','joystick.yaml')]
        ),


    
    ])
     




