#!/usr/bin/env python3
"""
simple_navigator.py - Dead simple cmd_vel navigator, no Nav2 needed.
"""
import rclpy, math, time, threading
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PolygonStamped
from std_msgs.msg import String
from std_srvs.srv import Trigger
from visualization_msgs.msg import MarkerArray, Marker
from geometry_msgs.msg import Point

STANDOFF   = 0.75
ADJ_OFFSET = 0.50

class SimpleNavigator(Node):
    def __init__(self):
        super().__init__('simple_navigator')
        self.x = self.y = self.yaw = 0.0
        self.corners = None
        self.walls = {}

        self.create_subscription(Odometry, '/odom', self._odom_cb, 10)
        self.create_subscription(PolygonStamped, '/wall_corners', self._corners_cb, 10)

        self.cmd_pub       = self.create_publisher(Twist, '/cmd_vel', 10)
        self.status_pub    = self.create_publisher(String, '/wall_selector/status', 10)
        self.goal_pub      = self.create_publisher(MarkerArray, '/goal_marker', 10)
        self.highlight_pub = self.create_publisher(MarkerArray, '/selected_wall', 10)

        self.create_service(Trigger, '/go_to_wall_A', lambda q,r: self._svc('A', r))
        self.create_service(Trigger, '/go_to_wall_B', lambda q,r: self._svc('B', r))
        self.create_service(Trigger, '/go_to_wall_C', lambda q,r: self._svc('C', r))
        self.create_service(Trigger, '/go_to_wall_D', lambda q,r: self._svc('D', r))

        self.get_logger().info('SimpleNavigator ready. Services: /go_to_wall_A/B/C/D')

    def _odom_cb(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        self.yaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y**2+q.z**2))

    def _corners_cb(self, msg):
        if len(msg.polygon.points) < 4: return
        pts = [(p.x, p.y) for p in msg.polygon.points]
        bl, br, tr, tl = pts
        self.corners = pts
        self.walls = {
            'A': {'gx': bl[0]+ADJ_OFFSET, 'gy': bl[1]+STANDOFF,  'gyaw':  0.0,       'name': 'South'},
            'B': {'gx': br[0]-STANDOFF,   'gy': tr[1]-ADJ_OFFSET, 'gyaw': -math.pi/2, 'name': 'East'},
            'C': {'gx': tr[0]-ADJ_OFFSET, 'gy': tr[1]-STANDOFF,   'gyaw':  math.pi,   'name': 'North'},
            'D': {'gx': tl[0]+STANDOFF,   'gy': bl[1]+ADJ_OFFSET, 'gyaw':  math.pi/2, 'name': 'West'},
        }
        self.get_logger().info(f'Corners: BL{bl} BR{br} TR{tr} TL{tl}')
        self.get_logger().info(f'B East goal: ({self.walls["B"]["gx"]:.2f}, {self.walls["B"]["gy"]:.2f})')

    def _svc(self, key, response):
        threading.Thread(target=self._navigate, args=(key,), daemon=True).start()
        response.success = True
        response.message = f'Navigating to wall {key}'
        return response

    def _navigate(self, key):
        for _ in range(60):
            if self.corners: break
            time.sleep(0.5)
        if not self.corners:
            self.get_logger().error('No corners — call /detect_walls first')
            return

        w = self.walls[key]
        gx, gy, gyaw = w['gx'], w['gy'], w['gyaw']
        self.get_logger().info(f'→ {w["name"]} wall: odom goal ({gx:.2f},{gy:.2f}) yaw={math.degrees(gyaw):.0f}°')

        self._pub_goal_marker(gx, gy, gyaw)
        self._pub_highlight(key)

        # Rotate toward goal
        self._rotate_to(math.atan2(gy-self.y, gx-self.x))
        # Drive to goal
        self._drive_to(gx, gy)
        # Final rotation
        self._rotate_to(gyaw)
        self._stop()

        self.get_logger().info(f'✓ Arrived at {w["name"]} wall! pos=({self.x:.2f},{self.y:.2f})')
        msg = String(); msg.data = f'arrived:{key}'
        for _ in range(120):
            self.status_pub.publish(msg)
            self._stop()
            time.sleep(0.5)

    def _rotate_to(self, target_yaw, tol=0.08):
        self.get_logger().info(f'Rotating to {math.degrees(target_yaw):.1f}°')
        for _ in range(400):
            err = self._adiff(target_yaw, self.yaw)
            if abs(err) < tol: break
            t = Twist(); t.angular.z = max(-0.5, min(0.5, 1.5*err))
            self.cmd_pub.publish(t)
            time.sleep(0.05)
        self._stop(); time.sleep(0.3)

    def _drive_to(self, gx, gy, tol=0.25):
        self.get_logger().info(f'Driving to ({gx:.2f},{gy:.2f})')
        for i in range(1200):
            dx=gx-self.x; dy=gy-self.y
            dist=math.sqrt(dx**2+dy**2)
            if dist < tol:
                self.get_logger().info(f'Reached! dist={dist:.3f}m'); break
            heading_err = self._adiff(math.atan2(dy,dx), self.yaw)
            t = Twist()
            t.linear.x  = min(0.25, 0.5*dist)
            t.angular.z = max(-0.8, min(0.8, 2.0*heading_err))
            self.cmd_pub.publish(t)
            if i % 40 == 0:
                self.get_logger().info(f'  dist={dist:.2f}m @ ({self.x:.2f},{self.y:.2f})')
            time.sleep(0.05)
        self._stop()

    def _stop(self):
        t = Twist()
        for _ in range(5): self.cmd_pub.publish(t); time.sleep(0.02)

    def _adiff(self, a, b):
        d = a-b
        while d > math.pi: d -= 2*math.pi
        while d < -math.pi: d += 2*math.pi
        return d

    def _pub_goal_marker(self, gx, gy, gyaw):
        ma = MarkerArray(); now = self.get_clock().now().to_msg()
        mk = Marker(); mk.header.frame_id='map'; mk.header.stamp=now
        mk.ns='goal'; mk.id=0; mk.type=Marker.ARROW; mk.action=Marker.ADD
        mk.pose.position.x=gx; mk.pose.position.y=gy; mk.pose.position.z=0.5
        mk.pose.orientation.z=math.sin(gyaw/2); mk.pose.orientation.w=math.cos(gyaw/2)
        mk.scale.x=1.0; mk.scale.y=0.2; mk.scale.z=0.2
        mk.color.r=0.0; mk.color.g=0.8; mk.color.b=1.0; mk.color.a=1.0
        ma.markers.append(mk)
        txt=Marker(); txt.header.frame_id='map'; txt.header.stamp=now
        txt.ns='goal'; txt.id=1; txt.type=Marker.TEXT_VIEW_FACING; txt.action=Marker.ADD
        txt.pose.position.x=gx; txt.pose.position.y=gy; txt.pose.position.z=1.2
        txt.pose.orientation.w=1.0; txt.scale.z=0.4
        txt.color.r=1.0; txt.color.g=1.0; txt.color.b=0.0; txt.color.a=1.0
        txt.text=f'GOAL\n({gx:.2f},{gy:.2f})'
        ma.markers.append(txt)
        self.goal_pub.publish(ma)

    def _pub_highlight(self, key):
        if not self.corners: return
        bl,br,tr,tl = self.corners
        segs={'A':[bl,br],'B':[br,tr],'C':[tr,tl],'D':[tl,bl]}
        ma=MarkerArray(); now=self.get_clock().now().to_msg()
        mk=Marker(); mk.header.frame_id='map'; mk.header.stamp=now
        mk.ns='selected'; mk.id=0; mk.type=Marker.LINE_STRIP; mk.action=Marker.ADD
        mk.scale.x=0.12
        mk.color.r=0.0; mk.color.g=1.0; mk.color.b=1.0; mk.color.a=1.0
        for px,py in segs[key]:
            for z in [0.0,2.7]:
                p=Point(); p.x=float(px); p.y=float(py); p.z=z
                mk.points.append(p)
        ma.markers.append(mk)
        self.highlight_pub.publish(ma)


def main(args=None):
    rclpy.init(args=args)
    node = SimpleNavigator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
