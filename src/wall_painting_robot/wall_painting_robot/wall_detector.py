#!/usr/bin/env python3
"""
wall_detector.py
Detects the 4 walls of a rectangular room from the 2D occupancy map.
Room is ~3.2m x 3.0m. Publishes wall corners and markers.
"""
import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PolygonStamped, Point32
from visualization_msgs.msg import MarkerArray, Marker
from std_srvs.srv import Trigger
import numpy as np

class WallDetector(Node):
    def __init__(self):
        super().__init__('wall_detector')
        self.map_data = None
        self.map_info = None
        self.corners = None

        self.map_sub = self.create_subscription(
            OccupancyGrid, '/map', self.map_callback, 10)
        self.corners_pub = self.create_publisher(
            PolygonStamped, '/wall_corners', 10)
        self.wall_markers_pub = self.create_publisher(
            MarkerArray, '/wall_markers', 10)
        self.floor_markers_pub = self.create_publisher(
            MarkerArray, '/floor_markers', 10)
        self.detect_srv = self.create_service(
            Trigger, '/detect_walls', self.detect_callback)

        self.get_logger().info('WallDetector ready. Call /detect_walls to detect.')

    def map_callback(self, msg):
        self.map_data = msg
        self.map_info = msg.info

    def detect_callback(self, request, response):
        if self.map_data is None:
            response.success = False
            response.message = 'No map received yet'
            return response

        try:
            self.detect_walls()
            response.success = True
            response.message = f'Detected room corners: {self.corners}'
        except Exception as e:
            response.success = False
            response.message = str(e)
        return response

    def detect_walls(self):
        info = self.map_info
        data = np.array(self.map_data.data).reshape(info.height, info.width)

        # Find occupied cells (walls = value > 50)
        occupied = (data > 50)

        # Find bounding box of occupied region
        rows = np.any(occupied, axis=1)
        cols = np.any(occupied, axis=0)
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]

        res = info.resolution
        ox  = info.origin.position.x
        oy  = info.origin.position.y

        # Convert to world coordinates
        x_min = ox + cmin * res
        x_max = ox + cmax * res
        y_min = oy + rmin * res
        y_max = oy + rmax * res

        wall_h = 2.7  # room height metres

        # BL, BR, TR, TL
        self.corners = [
            (x_min, y_min), (x_max, y_min),
            (x_max, y_max), (x_min, y_max)
        ]
        bl, br, tr, tl = self.corners

        w = abs(x_max - x_min)
        h = abs(y_max - y_min)
        self.get_logger().info(
            f'Room: {w:.2f}m x {h:.2f}m x {wall_h}m')
        self.get_logger().info(
            f'BL={bl} BR={br} TR={tr} TL={tl}')

        # Publish corners
        poly = PolygonStamped()
        poly.header.frame_id = 'map'
        poly.header.stamp = self.get_clock().now().to_msg()
        for (px, py) in self.corners:
            pt = Point32(); pt.x = float(px); pt.y = float(py); pt.z = 0.0
            poly.polygon.points.append(pt)
        self.corners_pub.publish(poly)

        # Publish wall markers
        self.publish_wall_markers(bl, br, tr, tl, wall_h)
        self.publish_floor_markers(bl, br, tr, tl)

    def publish_wall_markers(self, bl, br, tr, tl, wall_h):
        ma = MarkerArray()
        walls = [
            ('A_south', bl, br),
            ('B_east',  br, tr),
            ('C_north', tr, tl),
            ('D_west',  tl, bl),
        ]
        now = self.get_clock().now().to_msg()
        for i, (name, p1, p2) in enumerate(walls):
            mk = Marker()
            mk.header.frame_id = 'map'
            mk.header.stamp = now
            mk.ns = 'walls'; mk.id = i
            mk.type = Marker.LINE_STRIP
            mk.action = Marker.ADD
            mk.scale.x = 0.05
            mk.color.r = 1.0; mk.color.g = 1.0; mk.color.b = 0.0; mk.color.a = 1.0
            from geometry_msgs.msg import Point
            for px, py in [p1, p2]:
                for z in [0.0, wall_h]:
                    pt = Point(); pt.x = float(px); pt.y = float(py); pt.z = z
                    mk.points.append(pt)
            ma.markers.append(mk)

            # Corner sphere
            sp = Marker()
            sp.header.frame_id = 'map'; sp.header.stamp = now
            sp.ns = 'corners'; sp.id = 10+i
            sp.type = Marker.SPHERE; sp.action = Marker.ADD
            sp.pose.position.x = float(p1[0])
            sp.pose.position.y = float(p1[1])
            sp.pose.position.z = wall_h
            sp.pose.orientation.w = 1.0
            sp.scale.x = sp.scale.y = sp.scale.z = 0.3
            sp.color.r = 1.0; sp.color.g = 0.5; sp.color.b = 0.0; sp.color.a = 1.0
            sp.text = name
            ma.markers.append(sp)
        self.wall_markers_pub.publish(ma)

    def publish_floor_markers(self, bl, br, tr, tl):
        ma = MarkerArray()
        now = self.get_clock().now().to_msg()
        mk = Marker()
        mk.header.frame_id = 'map'; mk.header.stamp = now
        mk.ns = 'floor'; mk.id = 0
        mk.type = Marker.LINE_STRIP; mk.action = Marker.ADD
        mk.scale.x = 0.03
        mk.color.r = 0.8; mk.color.g = 0.0; mk.color.b = 0.0; mk.color.a = 0.8
        from geometry_msgs.msg import Point
        for px, py in [bl, br, tr, tl, bl]:
            pt = Point(); pt.x = float(px); pt.y = float(py); pt.z = 0.01
            mk.points.append(pt)
        ma.markers.append(mk)
        self.floor_markers_pub.publish(ma)


def main(args=None):
    rclpy.init(args=args)
    node = WallDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
