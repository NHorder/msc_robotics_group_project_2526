import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, SetEnvironmentVariable, IncludeLaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    urdfPath = os.path.join(FindPackageShare('wall_painting_robot').find('wall_painting_robot'), 'urdf', 'rover', 'model.sdf')

    return LaunchDescription([
        # Declare launch arguments
        DeclareLaunchArgument('x', default_value='0', description='X position of the robot'),
        DeclareLaunchArgument('y', default_value='0', description='Y position of the robot'),
        DeclareLaunchArgument('z', default_value='0.15', description='Z position of the robot'),
        DeclareLaunchArgument('roll', default_value='0', description='Roll of the robot'),
        DeclareLaunchArgument('pitch', default_value='0', description='Pitch of the robot'),
        DeclareLaunchArgument('yaw', default_value='0', description='Yaw of the robot'),
        DeclareLaunchArgument('robot_name', default_value='wall_painting_robot', description='Robot name'),
        DeclareLaunchArgument('world_file', default_value=LaunchConfiguration('world_file', default=os.path.join(FindPackageShare('wall_painting_robot').find('wall_painting_robot'), 'worlds', 'ground_floor.world')),
                               description='World file for the simulation'),
        DeclareLaunchArgument('robot_description', default_value=os.path.join(FindPackageShare('wall_painting_robot').find('wall_painting_robot'), 'urdf', 'rover.sdf')),
 

        GroupAction([
            # Set gazebo env variable
            SetEnvironmentVariable("IGN_GAZEBO_RESOURCE_PATH",value = PathJoinSubstitution([FindPackageShare('wall_painting_robot'),"worlds"])),
            

            # Launch gazebo with correct world       
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(os.path.join(FindPackageShare('ros_gz_sim').find('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
                launch_arguments={
                    'gz_args': [LaunchConfiguration('world_file'), ' -r'],
                    'on_exit_shutdown': 'true',
                }.items()
            ),
        ]),


        # Launch gazebo/ROS2 bridge
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            output='screen',
            parameters=[
                {"config_file": os.path.join(FindPackageShare('wall_painting_robot').find('wall_painting_robot'), 'config', 'gazebo_bridge.yaml')}
            ]
        ),

        # Launch image bridge
        Node(
            package='ros_gz_image',
            executable='image_bridge',
            arguments=["camera"],
            remappings=[
                ('/camera', '/camera/image_raw'),
                ('/camera/compressed', '/camera/image_raw/compressed'),
            ],
            parameters=[
                {"qos": "sensor_data"}
            ]
        ),

        # Spawn sdf
        Node(package='ros_gz_sim', executable='create',
            arguments=['-name', 'wall_painting_robot',
                # Default spawn point
                # '-x', '1.8',
                # '-y', '-3.4',
                # '-z', '3.0',
                # '-Y', '1.57'

                # In front of a QR code
                #'-x', '-3.3466',
                #'-y', '-0.6789',
                #'-z', '3.0',
                #'-Y', '3.0591',
                
                '-x', '2.0',
        	'-y', '2.0',
        	'-z', '0.1',
        	'-Y', '0.0',
                '-file', urdfPath],
            output='screen'),

        # Robot state publisher node
        Node(package='robot_state_publisher', executable='robot_state_publisher',
            output='screen',
            parameters = [
                # {'ignore_timestamp': False},
                # {'frame_prefix': 'wall_painting_robot/'},
                {'use_sim_time': True},
                {'robot_description': open(urdfPath).read()}],
        ),
        
        Node(
	    package='wall_painting_robot',
	    executable='odom_to_tf',
	    name='odom_to_tf',
	    output='screen'
	)


    ])
