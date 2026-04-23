import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, SetEnvironmentVariable, IncludeLaunchDescription, TimerAction
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    urdfPath = os.path.join(FindPackageShare('wall_painting_robot').find('wall_painting_robot'), 'urdf', 'rover', 'model.sdf')

    return LaunchDescription([
        DeclareLaunchArgument('x', default_value='0', description='X position of the robot'),
        DeclareLaunchArgument('y', default_value='0', description='Y position of the robot'),
        DeclareLaunchArgument('z', default_value='0.15', description='Z position of the robot'),
        DeclareLaunchArgument('roll', default_value='0', description='Roll of the robot'),
        DeclareLaunchArgument('pitch', default_value='0', description='Pitch of the robot'),
        DeclareLaunchArgument('yaw', default_value='0', description='Yaw of the robot'),
        DeclareLaunchArgument('robot_name', default_value='wall_painting_robot', description='Robot name'),
        DeclareLaunchArgument('world_file',
            default_value=LaunchConfiguration('world_file', default=os.path.join(
                FindPackageShare('wall_painting_robot').find('wall_painting_robot'),
                'worlds', 'one_room.world')),
            description='World file for the simulation'),
        DeclareLaunchArgument('robot_description',
            default_value=os.path.join(
                FindPackageShare('wall_painting_robot').find('wall_painting_robot'),
                'urdf', 'rover.sdf')),

        GroupAction([
            SetEnvironmentVariable("IGN_GAZEBO_RESOURCE_PATH",
                value=PathJoinSubstitution([FindPackageShare('wall_painting_robot'), "worlds"])),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(os.path.join(
                    FindPackageShare('ros_gz_sim').find('ros_gz_sim'),
                    'launch', 'gz_sim.launch.py')),
                launch_arguments={
                    'gz_args': [LaunchConfiguration('world_file'), ' -r'],
                    'on_exit_shutdown': 'true',
                }.items()
            ),
        ]),

        # Gazebo/ROS2 bridge
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            output='screen',
            parameters=[{"config_file": os.path.join(
                FindPackageShare('wall_painting_robot').find('wall_painting_robot'),
                'config', 'gazebo_bridge.yaml')}]
        ),

        # Spawn robot - delayed to wait for Gazebo to load
        TimerAction(
            period=5.0,  # Wait 5 seconds for Gazebo to be ready
            actions=[
                Node(package='ros_gz_sim', executable='create',
                    arguments=[
                        '-name', 'wall_painting_robot',
                        '-x', '5.815',
                        '-y', '9.215',
                        '-z', '0.1',
                        '-Y', '-1.5708',
                        '-file', urdfPath],
                    output='screen'),
            ]
        ),

        # Robot state publisher
        Node(package='robot_state_publisher', executable='robot_state_publisher',
            output='screen',
            parameters=[
                {'use_sim_time': True},
                {'robot_description': open(urdfPath).read()}]),

        # NOTE: odom_to_tf is launched by navigation_launch.py — NOT here
    ])
