import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg = FindPackageShare('wall_painting_robot').find('wall_painting_robot')
    rviz_config = os.path.join(pkg, 'config', 'mapping.rviz')

    return LaunchDescription([

        # ── Simulation ──────────────────────────────────────────────────
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg, 'launch', 'simulation.launch.py')
            )
        ),

        # ── Joint State Publisher — needed so RSP doesn't publish garbage
        #    transforms for manipulator links during SLAM (caused map shift)
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': True}],
        ),

        # ── SLAM Toolbox (2D map from LiDAR) ────────────────────────────
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[
                {'use_sim_time': True},
                os.path.join(pkg, 'config', 'slam_toolbox.yaml')
            ]
        ),

        # ── Octomap DISABLED during mapping ─────────────────────────────
        # Octomap sees the robot's own body (manipulator + screen pole)
        # causing white dots inside the map. Not needed for 2D SLAM.
        # Re-enable after mapping is complete if needed for 3D visualization.
        #
        # Node(
        #     package='octomap_server',
        #     executable='octomap_server_node',
        #     ...
        # ),

        # ── Wall Detector ────────────────────────────────────────────────
        #Node(
        #    package='wall_painting_robot',
        #    executable='wall_detector',
        #    name='wall_detector',
        #    output='screen',
        #    parameters=[{'use_sim_time': True}]
        #),

        # ── RViz ─────────────────────────────────────────────────────────
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
        ),
    ])
