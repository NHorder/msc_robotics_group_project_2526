#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

class OdomToTFNode(Node):
    def __init__(self):
        super().__init__('odom_to_tf_node')

        self.tf_broadcaster = TransformBroadcaster(self)

        # Subscribe to odometry topic
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.get_logger().info('Odom to TF node started.')

    def odom_callback(self, msg: Odometry):
        # Create a transform message
        t = TransformStamped()

        # Set header info
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = msg.header.frame_id  # typically "odom"
        t.child_frame_id = msg.child_frame_id if msg.child_frame_id else "base_link"

        # Set translation
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z

        # Set rotation
        t.transform.rotation = msg.pose.pose.orientation

        # Publish the transform
        self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = OdomToTFNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()

if __name__ == '__main__':
    main()
