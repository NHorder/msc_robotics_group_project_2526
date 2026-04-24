#!/usr/bin/env python3
"""
wall_painter.py — Simple feedback-based wall painter.

Strategy:
  - j1=0, j5=0 always (no yaw, no roll)
  - j2, j4 fixed constants (arm pointed at wall)
  - ONLY j3 moves: sweeps -0.70 → -2.80 (down) then -2.80 → -0.70 (up)
  - Feedback: only advance when j3 reaches target within THRESHOLD
  - New SDF: no arm collision → arm passes through wall freely
  - Base mass=200 → cannot tip
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64, String
from sensor_msgs.msg import JointState
from geometry_msgs.msg import PoseWithCovarianceStamped, PolygonStamped
from visualization_msgs.msg import MarkerArray, Marker
from nav_msgs.msg import Odometry
import math, time, threading

# ── Fixed joint values ────────────────────────────────────────────────────────
J1 = 0.0      # no yaw
J2 = 0.25     # shoulder — reduced to prevent over-extension
J4 = 0.50     # wrist — adjusted for reduced J2
J5 = 0.0      # no roll

# ── j3 sweep range (SDF limits: lower=-3.0543, upper=-0.6557) ────────────────
J3_TOP = -0.70    # top of stroke
J3_BOT = -2.80    # bottom of stroke
N_STEPS = 80      # waypoints per stroke

# ── Control ───────────────────────────────────────────────────────────────────
THRESHOLD  = 0.15   # rad — advance when j3 within this of target
PAUSE_SECS = 2.0    # pause at bottom before reversing

J3_DOWN = [J3_TOP + i * (J3_BOT - J3_TOP) / (N_STEPS - 1) for i in range(N_STEPS)]
J3_UP   = list(reversed(J3_DOWN))
J3_ALL  = J3_DOWN + J3_UP
N_ALL   = len(J3_ALL)


class WallPainter(Node):
    def __init__(self):
        super().__init__('wall_painter')
        self.declare_parameter('wall_key', '')
        self._wall_key = self.get_parameter('wall_key').get_parameter_value().string_value

        self._corners   = None
        self._pose      = None
        self._robot_yaw = 0.0
        self._pid       = 0
        self._j3_actual = J3_TOP
        self._step      = 0
        self._active    = False

        self.create_subscription(PolygonStamped, '/wall_corners', self._corners_cb, 10)
        self.create_subscription(PoseWithCovarianceStamped, '/amcl_pose', self._pose_cb, 10)
        self.create_subscription(Odometry, '/odom', self._odom_cb, 10)
        self.create_subscription(String, '/wall_selector/status', self._status_cb, 10)
        self.create_subscription(JointState,
            '/model/wall_painting_robot/joint_states', self._js_cb, 10)

        base = '/model/wall_painting_robot'
        self._jpub = [self.create_publisher(Float64, f'{base}/joint{i}/cmd_pos', 10)
                      for i in range(1, 6)]
        self._done_pub  = self.create_publisher(String, '/wall_painter/status', 10)
        self._paint_pub = self.create_publisher(MarkerArray, '/paint_marks', 10)

        self.create_timer(0.02, self._control_cb)

        if self._wall_key:
            threading.Thread(target=self._start, args=(self._wall_key,), daemon=True).start()

        self.get_logger().info(
            f'WallPainter ready. {N_ALL} steps, j3: {J3_TOP}→{J3_BOT}→{J3_TOP}')

    def _js_cb(self, msg):
        for name, pos in zip(msg.name, msg.position):
            if name == 'manip_joint3':
                self._j3_actual = pos

    def _pose_cb(self, msg):
        self._pose = msg.pose.pose
        q = msg.pose.pose.orientation
        self._robot_yaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y**2+q.z**2))

    def _odom_cb(self, msg):
        if not self._pose:
            self._pose = msg.pose.pose
            q = msg.pose.pose.orientation
            self._robot_yaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y**2+q.z**2))

    def _corners_cb(self, msg):
        if len(msg.polygon.points) >= 4:
            self._corners = [(p.x, p.y) for p in msg.polygon.points]

    def _status_cb(self, msg):
        if msg.data.startswith('arrived:') and not self._active:
            key = msg.data.split(':')[1].strip()
            threading.Thread(target=self._start, args=(key,), daemon=True).start()

    def _control_cb(self):
        j3_cmd = J3_ALL[self._step] if (self._active and self._step < N_ALL) else J3_TOP
        for i, v in enumerate([J1, J2, j3_cmd, J4, J5]):
            m = Float64(); m.data = float(v)
            self._jpub[i].publish(m)

        if not self._active:
            return

        if abs(self._j3_actual - j3_cmd) < THRESHOLD:
            self._paint_mark(j3_cmd)

            if self._step == 0:
                self.get_logger().info('Sweep 1 START: top → bottom')
            elif self._step == N_STEPS - 1:
                self._step += 1
                self.get_logger().info('Sweep 1 END. Pausing...')
                self._active = False
                threading.Thread(target=self._pause_and_resume, daemon=True).start()
                return
            elif self._step == N_STEPS:
                self.get_logger().info('Sweep 2 START: bottom → top')

            self._step += 1

            if self._step >= N_ALL:
                self._active = False
                self.get_logger().info('2 sweeps DONE!')
                m = String(); m.data = f'done:{self._wall_key}'
                self._done_pub.publish(m)

    def _pause_and_resume(self):
        time.sleep(PAUSE_SECS)
        self.get_logger().info('Resuming sweep 2')
        self._active = True

    def _start(self, key):
        self._wall_key = key
        for _ in range(20):
            time.sleep(0.5)
            if self._pose: break
        if not self._corners:
            import subprocess
            subprocess.Popen(['ros2', 'service', 'call', '/detect_walls',
                              'std_srvs/srv/Trigger', '{}'])
            for _ in range(10):
                time.sleep(0.5)
                if self._corners: break
        self.get_logger().info(f'Starting wall {key}')
        self._step  = 0
        self._active = True

    def _paint_mark(self, j3):
        if not self._pose:
            return
        frac = (j3 - J3_TOP) / (J3_BOT - J3_TOP)
        frac = max(0.0, min(1.0, frac))
        z    = 0.20 + (1.0 - frac) * 2.30

        yaw   = self._robot_yaw
        fwd_x = math.cos(yaw); fwd_y = math.sin(yaw)
        px    = self._pose.position.x; py = self._pose.position.y

        if self._corners and len(self._corners) >= 4:
            xs = [c[0] for c in self._corners]; ys = [c[1] for c in self._corners]
            cands = []
            if abs(fwd_x) > 0.01:
                d = ((max(xs) if fwd_x > 0 else min(xs)) - px) / fwd_x
                if d > 0.1: cands.append(d)
            if abs(fwd_y) > 0.01:
                d = ((max(ys) if fwd_y > 0 else min(ys)) - py) / fwd_y
                if d > 0.1: cands.append(d)
            D = min(cands) if cands else 1.0
        else:
            D = 1.0

        mk = Marker()
        mk.header.frame_id = 'map'
        mk.header.stamp    = self.get_clock().now().to_msg()
        mk.ns = 'paint'; mk.id = self._pid; self._pid += 1
        mk.type = Marker.CUBE; mk.action = Marker.ADD
        mk.lifetime.sec = 0
        mk.pose.orientation.w = 1.0
        mk.color.r = 1.0; mk.color.g = 1.0; mk.color.b = 0.0; mk.color.a = 1.0
        mk.pose.position.x = px + fwd_x * D
        mk.pose.position.y = py + fwd_y * D
        mk.pose.position.z = z
        mk.scale.x = 0.04; mk.scale.y = 0.28; mk.scale.z = 0.08
        ma = MarkerArray(); ma.markers.append(mk)
        self._paint_pub.publish(ma)


def main(args=None):
    rclpy.init(args=args)
    node = WallPainter()
    rclpy.spin(node)
    node.destroy_node()
    try: rclpy.shutdown()
    except Exception: pass


if __name__ == '__main__':
    main()
