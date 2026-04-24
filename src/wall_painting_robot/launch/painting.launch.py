from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    wall_key_arg = DeclareLaunchArgument(
        'wall_key', default_value='A',
        description='Wall: A=South B=East C=North D=West')

    # Trigger wall detection so corners are available
    detect = ExecuteProcess(
        cmd=['ros2', 'service', 'call', '/detect_walls',
             'std_srvs/srv/Trigger', '{}'], output='screen')

    detect_retry = TimerAction(period=2.0, actions=[
        ExecuteProcess(
            cmd=['ros2', 'service', 'call', '/detect_walls',
                 'std_srvs/srv/Trigger', '{}'], output='screen')])

    # Wall painter — starts 5s after detect
    painter = TimerAction(period=5.0, actions=[
        Node(package='wall_painting_robot', executable='wall_painter',
             name='wall_painter', output='screen',
             parameters=[{'wall_key': LaunchConfiguration('wall_key')}])])

    return LaunchDescription([wall_key_arg, detect, detect_retry, painter])
