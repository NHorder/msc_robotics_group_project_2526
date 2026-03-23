import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    pkg_path = FindPackageShare('wall_painting_robot').find('wall_painting_robot')

    return LaunchDescription([

        # ----------------------------------------------------------------
        # TELEOPERATION
        # ----------------------------------------------------------------
        # Launch teleop_keyboard
         Node(
             package='teleop_twist_keyboard',
             executable='teleop_twist_keyboard',
             name='teleop',
             output='screen',
             prefix = 'xterm -e',
         ),

        # Controller
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg_path, 'launch', 'joystick.launch.py')),
        ),


        # ----------------------------------------------------------------
        # VISUALISATION
        # ----------------------------------------------------------------
        # Launch rqt_image_view to show the output
        Node(
	    package='rqt_image_view',
	    executable='rqt_image_view',
	    name='camera_view',
	    output='screen',
	    arguments=['/camera/image_raw'],
	)


    ])
     




