from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    wall_key_arg = DeclareLaunchArgument('wall_key', default_value='B')

    mv_pkg = get_package_share_directory('visnat_moveit_config')
    wp_pkg = get_package_share_directory('wall_painting_robot')

    urdf_file = os.path.join(wp_pkg, 'urdf', 'visnat.urdf')
    srdf_file = os.path.join(mv_pkg, 'config', 'visnat.srdf')

    with open(urdf_file, 'r') as f:
        robot_description = f.read()
    with open(srdf_file, 'r') as f:
        robot_description_semantic = f.read()

    # Detect walls
    detect = ExecuteProcess(
        cmd=['ros2', 'service', 'call', '/detect_walls',
             'std_srvs/srv/Trigger', '{}'], output='screen')
    detect_retry = TimerAction(period=2.0, actions=[
        ExecuteProcess(
            cmd=['ros2', 'service', 'call', '/detect_walls',
                 'std_srvs/srv/Trigger', '{}'], output='screen')])

    # Controller config — tells MoveIt about our arm_controller
    moveit_controllers = {
        'moveit_controller_manager':
            'moveit_simple_controller_manager/MoveItSimpleControllerManager',
        'moveit_simple_controller_manager': {
            'controller_names': ['arm_controller'],
        },
        'arm_controller': {
            'type': 'FollowJointTrajectory',
            'action_ns': 'follow_joint_trajectory',
            'default': True,
            'joints': [
                'manip_joint1', 'manip_joint2', 'manip_joint3',
                'manip_joint4', 'manip_joint5'
            ]
        }
    }

    move_group = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        remappings=[
            ('joint_states', '/model/wall_painting_robot/joint_states'),
        ],
        parameters=[
            {
                'robot_description': robot_description,
                'robot_description_semantic': robot_description_semantic,
                'use_sim_time': True,
                'publish_planning_scene': True,
                'publish_geometry_updates': True,
                'publish_state_updates': True,
                'publish_transforms_updates': True,
                'robot_description_kinematics': {
                    'arm': {
                        'kinematics_solver':
                            'kdl_kinematics_plugin/KDLKinematicsPlugin',
                        'kinematics_solver_search_resolution': 0.005,
                        'kinematics_solver_timeout': 0.05,
                    }
                },
            },
            moveit_controllers,
        ]
    )

    painter = TimerAction(period=10.0, actions=[
        Node(
            package='wall_painting_robot',
            executable='cartesian_painter',
            name='cartesian_painter',
            output='screen',
            parameters=[{'wall_key': LaunchConfiguration('wall_key')}]
        )
    ])

    return LaunchDescription([
        wall_key_arg,
        detect,
        detect_retry,
        move_group,
        painter,
    ])
