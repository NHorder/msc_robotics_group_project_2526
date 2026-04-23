#!/usr/bin/env python3
"""
trajectory_bridge.py

Bridges MoveIt's FollowJointTrajectory action to Gazebo's
individual joint cmd_pos topics.

MoveIt sends: /arm_controller/follow_joint_trajectory (action)
Gazebo uses:  /model/wall_painting_robot/joint{1-5}/cmd_pos (Float64)
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from control_msgs.action import FollowJointTrajectory
from std_msgs.msg import Float64
import time
import threading


JOINT_NAMES = [
    'manip_joint1', 'manip_joint2', 'manip_joint3',
    'manip_joint4', 'manip_joint5'
]

BASE = '/model/wall_painting_robot'


class TrajectoryBridge(Node):
    def __init__(self):
        super().__init__('trajectory_bridge')

        # Publishers for each joint
        self._jpub = {}
        for i, name in enumerate(JOINT_NAMES):
            topic = f'{BASE}/joint{i+1}/cmd_pos'
            self._jpub[name] = self.create_publisher(Float64, topic, 10)

        # Action server
        self._action_server = ActionServer(
            self,
            FollowJointTrajectory,
            '/arm_controller/follow_joint_trajectory',
            execute_callback=self._execute_cb,
            goal_callback=self._goal_cb,
            cancel_callback=self._cancel_cb,
        )

        self.get_logger().info('TrajectoryBridge ready.')

    def _goal_cb(self, goal_request):
        self.get_logger().info('Received trajectory goal')
        return GoalResponse.ACCEPT

    def _cancel_cb(self, goal_handle):
        return CancelResponse.ACCEPT

    def _execute_cb(self, goal_handle):
        traj = goal_handle.request.trajectory
        points = traj.joint_trajectory.points
        joint_names = traj.joint_trajectory.joint_names

        self.get_logger().info(
            f'Executing trajectory: {len(points)} points, '
            f'joints: {joint_names}')

        if not points:
            goal_handle.succeed()
            return FollowJointTrajectory.Result()

        start_time = time.time()

        for i, point in enumerate(points):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                return FollowJointTrajectory.Result()

            # Publish each joint position
            for j, jname in enumerate(joint_names):
                if jname in self._jpub and j < len(point.positions):
                    m = Float64()
                    m.data = float(point.positions[j])
                    self._jpub[jname].publish(m)

            # Wait until next point's time
            if i < len(points) - 1:
                next_t = points[i+1].time_from_start.sec + \
                         points[i+1].time_from_start.nanosec * 1e-9
                curr_t = point.time_from_start.sec + \
                         point.time_from_start.nanosec * 1e-9
                dt = next_t - curr_t
                if dt > 0:
                    time.sleep(dt)

        self.get_logger().info('Trajectory execution complete')
        goal_handle.succeed()
        return FollowJointTrajectory.Result()


def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryBridge()
    rclpy.spin(node)
    node.destroy_node()
    try:
        rclpy.shutdown()
    except Exception:
        pass


if __name__ == '__main__':
    main()
