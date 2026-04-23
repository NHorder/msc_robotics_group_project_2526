#!/usr/bin/env python3
"""
wall_selector.py
Navigate robot to the START position for painting a selected wall.

Goal position rules:
  - 75 cm away from the selected wall (standoff)
  - 50 cm away from the adjacent wall (left end of wall = start of painting)

After arriving:
  - Publishes zero velocity at 10Hz to hold position
  - Republishes 'arrived:X' every 1s until wall_painter confirms
"""
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PolygonStamped, PoseWithCovarianceStamped, Twist, Point
from visualization_msgs.msg import MarkerArray, Marker
from std_msgs.msg import String, Float64
import math, threading, time

STANDOFF   = 1.95
ADJ_OFFSET = 1.30

# Travel pose — arm position during navigation (bottom, pulled back)
#   j1=0, j2=0.30, j3=-2.55, j4=1.0, j5=0
TRAVEL_POSE = [0.0, 0.30, -2.55, 1.0, 0.0]

# Home/painting pose — same as travel (ready to paint from bottom)
HOME_POSE   = [0.0, 0.30, -2.55, 1.0, 0.0]


class WallSelector(Node):
    def __init__(self):
        super().__init__('wall_selector')

        self.corners   = None
        self.walls     = {}
        self.amcl_pose = None
        self.amcl_ok   = False
        self._arrived_key   = None
        self._arrived_timer = None
        self._stop_timer    = None
        self._goal_handle   = None
        self._joint_hold_timer = None
        self._joint_target  = TRAVEL_POSE[:]
        self._painting_active = False  # Flag to stop joint control during painting

        self.create_subscription(PolygonStamped, '/wall_corners', self.corners_cb, 10)
        self.create_subscription(PoseWithCovarianceStamped, '/amcl_pose', self.amcl_cb, 10)
        self.create_subscription(String, '/wall_painter/status', self.painter_cb, 10)

        self.nav_client    = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.status_pub    = self.create_publisher(String, '/wall_selector/status', 10)
        self.cmd_vel_pub   = self.create_publisher(Twist, 'cmd_vel', 10)
        self.highlight_pub = self.create_publisher(MarkerArray, '/selected_wall', 10)

        base = '/model/wall_painting_robot'
        self._jpub = [
            self.create_publisher(Float64, f'{base}/joint{i}/cmd_pos', 10)
            for i in range(1, 6)
        ]

        # Continuously publish joint targets at 20Hz to keep arm locked
        self._joint_hold_timer = self.create_timer(0.05, self._publish_joints)

        self.get_logger().info('WallSelector ready.')

    def amcl_cb(self, msg):
        self.amcl_pose = msg.pose.pose
        self.amcl_ok   = True

    def corners_cb(self, msg):
        if len(msg.polygon.points) < 4:
            return
        pts = [(p.x, p.y) for p in msg.polygon.points]
        bl, br, tr, tl = pts

        self.walls = {
            'A': {
                'name': 'South Wall',
                'nav_x': bl[0] + ADJ_OFFSET,
                'nav_y': bl[1] + STANDOFF,
                'yaw':   0.0,
                'length': abs(br[0] - bl[0]),
                'facing': 'north',
                'along_axis': 'x', 'along_sign': +1,
                'wall_y': bl[1],
            },
            'B': {
                'name': 'East Wall',
                'nav_x': br[0] - STANDOFF,
                'nav_y': tr[1] - ADJ_OFFSET,
                'yaw':   -math.pi / 2,
                'length': abs(tr[1] - br[1]),
                'facing': 'west',
                'along_axis': 'y', 'along_sign': -1,
                'wall_x': br[0],
            },
            'C': {
                'name': 'North Wall',
                'nav_x': tr[0] - ADJ_OFFSET,
                'nav_y': tr[1] - STANDOFF,
                'yaw':   math.pi,
                'length': abs(tl[0] - tr[0]),
                'facing': 'south',
                'along_axis': 'x', 'along_sign': -1,
                'wall_y': tr[1],
            },
            'D': {
                'name': 'West Wall',
                'nav_x': tl[0] + STANDOFF,
                'nav_y': tl[1] - ADJ_OFFSET,
                'yaw':   math.pi / 2,
                'length': abs(tl[1] - bl[1]),
                'facing': 'east',
                'along_axis': 'y', 'along_sign': -1,
                'wall_x': tl[0],
            },
        }
        self.corners = {'BL': bl, 'BR': br, 'TR': tr, 'TL': tl}

        w  = abs(br[0] - bl[0])
        h  = abs(tr[1] - br[1])
        self.get_logger().info(f'Room: {w:.2f}m x {h:.2f}m')
        for k, v in self.walls.items():
            self.get_logger().info(
                f'  [{k}] {v["name"]} L={v["length"]:.2f}m '
                f'target=({v["nav_x"]:.2f},{v["nav_y"]:.2f}) '
                f'yaw={math.degrees(v["yaw"]):.0f}°')

    def painter_cb(self, msg):
        """Handle messages from wall_painter/cartesian_painter."""
        data = msg.data
        if data.startswith('painting:') or data.startswith('started:'):
            # Painting started — STOP controlling arm so painter can take over
            self._painting_active = True
            self._cancel_all_timers()
            self.get_logger().info(f'Painter started: {data} — releasing arm control')
        elif data.startswith('done:'):
            # Painting done — can resume arm control if needed
            self._painting_active = False
            self.get_logger().info(f'Painter done: {data}')
            self._cancel_timers()

    def _cancel_timers(self):
        """Cancel arrived/stop timers but keep joint hold."""
        for attr in ['_stop_timer', '_arrived_timer']:
            t = getattr(self, attr, None)
            if t:
                t.cancel()
                setattr(self, attr, None)
        self._arrived_key = None

    def _cancel_all_timers(self):
        """Cancel ALL timers including joint hold — for when painter takes over."""
        for attr in ['_stop_timer', '_arrived_timer', '_joint_hold_timer']:
            t = getattr(self, attr, None)
            if t:
                t.cancel()
                setattr(self, attr, None)
        self._arrived_key = None
        self.get_logger().info('All timers cancelled — painter has arm control')

    def _hold_stop(self):
        self.cmd_vel_pub.publish(Twist())

    def _republish_arrived(self):
        if self._arrived_key:
            m = String(); m.data = f'arrived:{self._arrived_key}'
            self.status_pub.publish(m)

    def navigate_to(self, wall_key):
        wall = self.walls[wall_key]
        print(f'\n  Navigating to {wall["name"]}...')
        print(f'  Target: ({wall["nav_x"]:.2f}, {wall["nav_y"]:.2f})  yaw={math.degrees(wall["yaw"]):.0f}°')

        # Reset painting flag and restart joint hold if needed
        self._painting_active = False
        if self._joint_hold_timer is None:
            self._joint_hold_timer = self.create_timer(0.05, self._publish_joints)

        if not self.nav_client.wait_for_server(timeout_sec=10.0):
            print('  [!] Nav2 not available')
            return

        self.highlight_wall(wall_key)

        g = NavigateToPose.Goal()
        g.pose.header.frame_id = 'map'
        g.pose.header.stamp = self.get_clock().now().to_msg()
        g.pose.pose.position.x = wall['nav_x']
        g.pose.pose.position.y = wall['nav_y']
        yaw = wall['yaw']
        g.pose.pose.orientation.z = math.sin(yaw / 2)
        g.pose.pose.orientation.w = math.cos(yaw / 2)

        future = self.nav_client.send_goal_async(
            g, feedback_callback=self.feedback_cb)
        future.add_done_callback(
            lambda f: self.goal_response_cb(f, wall_key))

    def feedback_cb(self, fb):
        dist = fb.feedback.distance_remaining
        print(f'\r  Distance remaining: {dist:.2f}m    ', end='', flush=True)

    def goal_response_cb(self, future, wall_key):
        gh = future.result()
        if not gh.accepted:
            print('\n  [!] Goal REJECTED by Nav2.')
            print('  Possible causes:')
            print('    1. AMCL not converged — set 2D Pose Estimate in RViz first')
            print('    2. Goal position is inside an obstacle or outside map')
            print('    3. Nav2 costmap not ready yet — wait 5s and retry')
            wall = self.walls[wall_key]
            print(f'  Goal was: x={wall["nav_x"]:.3f} y={wall["nav_y"]:.3f}')
            print('  Try: ros2 topic echo /amcl_pose --once  (check if pose is valid)')
            print('  Retrying in 5 seconds...')
            threading.Timer(5.0, lambda: self.navigate_to(wall_key)).start()
            return
        print('\n  Goal ACCEPTED — navigating...')
        self._goal_handle = gh
        gh.get_result_async().add_done_callback(
            lambda f: self.result_cb(f, wall_key))

    def result_cb(self, future, wall_key):
        status = future.result().status
        wall   = self.walls[wall_key]
        if status == 4:
            print(f'\n  ✓ XY goal reached — rotating to face wall...')
            threading.Thread(
                target=self._finish_arrival,
                args=(wall_key,), daemon=True).start()
        else:
            print(f'\n  [!] Navigation failed (status {status}) — retrying in 5s...')
            threading.Timer(5.0, lambda: self.navigate_to(wall_key)).start()

    def _finish_arrival(self, wall_key):
        wall       = self.walls[wall_key]
        target_yaw = wall['yaw']
        dt         = 0.05
        timeout    = 15.0

        elapsed = 0.0
        while elapsed < timeout:
            if not self.amcl_pose:
                time.sleep(dt); elapsed += dt; continue

            q = self.amcl_pose.orientation
            cy = math.atan2(2*(q.w*q.z + q.x*q.y),
                            1 - 2*(q.y**2 + q.z**2))
            err = target_yaw - cy
            while err >  math.pi: err -= 2*math.pi
            while err < -math.pi: err += 2*math.pi

            if abs(err) < 0.08:
                break

            omega = max(-0.4, min(0.4, 2.0 * err))
            twist = Twist(); twist.angular.z = omega
            self.cmd_vel_pub.publish(twist)
            time.sleep(dt); elapsed += dt

        self.cmd_vel_pub.publish(Twist())
        time.sleep(0.5)

        print(f'  ✓ Arrived at {wall["name"]}! Facing wall.')
        print(f'  Arm is at home position (j2=0.30, j3=-2.55, j4=1.0)')
        print(f'  Ready to paint. In a new terminal run:')
        print(f'  ros2 launch wall_painting_robot moveit_painting.launch.py wall_key:={wall_key}')

        self._stop_timer    = self.create_timer(0.1, self._hold_stop)
        self._arrived_key   = wall_key
        self._arrived_timer = self.create_timer(1.0, self._republish_arrived)

    def _publish_joints(self):
        """Continuously publish joint targets at 20Hz to keep arm locked."""
        if self._painting_active:
            return  # Don't interfere with painter
        for i, val in enumerate(self._joint_target):
            m = Float64(); m.data = float(val)
            self._jpub[i].publish(m)

    def _send_arm_home(self):
        """Switch joint target to home pose — held continuously by timer."""
        self._joint_target = HOME_POSE[:]
        self.get_logger().info('Arm → HOME pose')

    def highlight_wall(self, wall_key):
        if not self.corners:
            return
        wall = self.walls[wall_key]
        ma   = MarkerArray()
        now  = self.get_clock().now().to_msg()

        mk = Marker()
        mk.header.frame_id = 'map'; mk.header.stamp = now
        mk.ns = 'selected'; mk.id = 0
        mk.type = Marker.LINE_STRIP; mk.action = Marker.ADD
        mk.scale.x = 0.08
        mk.color.r = 0.0; mk.color.g = 1.0; mk.color.b = 1.0; mk.color.a = 1.0
        corners = self.corners
        wall_corners = {
            'A': [corners['BL'], corners['BR']],
            'B': [corners['BR'], corners['TR']],
            'C': [corners['TR'], corners['TL']],
            'D': [corners['TL'], corners['BL']],
        }
        for px, py in wall_corners[wall_key]:
            pt = Point(); pt.x = float(px); pt.y = float(py); pt.z = 0.1
            mk.points.append(pt)
        ma.markers.append(mk)

        arrow = Marker()
        arrow.header.frame_id = 'map'; arrow.header.stamp = now
        arrow.ns = 'goal_pose'; arrow.id = 1
        arrow.type = Marker.ARROW; arrow.action = Marker.ADD
        arrow.pose.position.x = wall['nav_x']
        arrow.pose.position.y = wall['nav_y']
        arrow.pose.position.z = 0.3
        yaw = wall['yaw']
        arrow.pose.orientation.z = math.sin(yaw / 2)
        arrow.pose.orientation.w = math.cos(yaw / 2)
        arrow.scale.x = 0.6
        arrow.scale.y = 0.12
        arrow.scale.z = 0.12
        arrow.color.r = 0.0; arrow.color.g = 1.0; arrow.color.b = 0.0; arrow.color.a = 1.0
        ma.markers.append(arrow)

        sphere = Marker()
        sphere.header.frame_id = 'map'; sphere.header.stamp = now
        sphere.ns = 'goal_pose'; sphere.id = 2
        sphere.type = Marker.SPHERE; sphere.action = Marker.ADD
        sphere.pose.position.x = wall['nav_x']
        sphere.pose.position.y = wall['nav_y']
        sphere.pose.position.z = 0.3
        sphere.pose.orientation.w = 1.0
        sphere.scale.x = sphere.scale.y = sphere.scale.z = 0.2
        sphere.color.r = 0.0; sphere.color.g = 1.0; sphere.color.b = 0.0; sphere.color.a = 0.8
        ma.markers.append(sphere)

        self.highlight_pub.publish(ma)


def run_ui(node):
    """Simple terminal UI running in a thread."""
    while rclpy.ok():
        time.sleep(1.0)
        if node.corners is None:
            print('Waiting for wall data...')
            print('Run: ros2 service call /detect_walls std_srvs/srv/Trigger {}')
            time.sleep(3.0)
            continue

        print('\n' + '='*60)
        print('       WALL PAINTING ROBOT — WALL SELECTOR')
        print('='*60)
        rx = node.amcl_pose.position.x if node.amcl_pose else 0.0
        ry = node.amcl_pose.position.y if node.amcl_pose else 0.0
        status = '✓ LOCALIZED' if node.amcl_ok else '✗ NOT LOCALIZED'
        print(f'AMCL: {status}  Robot at ({rx:.2f}, {ry:.2f})')
        print('-'*60)

        for k in ['A', 'B', 'C', 'D']:
            w = node.walls[k]
            print(f'  [{k}] {w["name"]:<12} L={w["length"]:.2f}m  '
                  f'target=({w["nav_x"]:.2f},{w["nav_y"]:.2f})  '
                  f'yaw={math.degrees(w["yaw"]):.0f}°')
        print('\n  [Q] Quit')
        print('='*60)

        choice = input('Wall (A/B/C/D) or Q: ').strip().upper()
        if choice == 'Q':
            break
        if choice not in node.walls:
            print('Invalid choice')
            continue
        if not node.amcl_ok:
            print('  [!] AMCL not yet confirmed — trying anyway (Nav2 may still work)')

        node.navigate_to(choice)
        print('Navigating... (watching distance in this terminal)')


def main(args=None):
    rclpy.init(args=args)
    node = WallSelector()

    spin_t = threading.Thread(target=lambda: rclpy.spin(node), daemon=True)
    spin_t.start()

    try:
        run_ui(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    try:
        rclpy.shutdown()
    except Exception:
        pass


if __name__ == '__main__':
    main()
