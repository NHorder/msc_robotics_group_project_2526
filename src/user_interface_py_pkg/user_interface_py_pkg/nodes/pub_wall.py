################################
# pub_wall.py
# Part of the user_interface_py_pkg
#
# Part of Cranfield University MSC Robotics Group Project 2025-2026
################################

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Pub_Wall():
    """
    Class: Pub_Wall
    Purpose: Publishes wall selection from UI selection
    """
    
    def __init__(self):
        """
        Initialisation Method
        """
        super().__init__('ui/pub/wall')

        # Define publisher
        self.publisher = self.create_publisher(
            String,
            '',
            10
        )

        # Retain count of published items for debugging
        self.published_cnt = 0

        # Notify of active state
        self.get_logger().info("UI-PUB-WALL || Status: Active")
    
    def Publish(self,msg):
        """
        Method for publishing to the '' topic
        """
        # Increment count
        self.published_cnt += 1

        # Publish msg
        self.publisher.publish(msg)

        # Notify of published info
        self.get_logger().info(f"UI-PUB-WALL // Published: {msg.data}")

    def NotifyDestruction(self):
        """
        Method that notifies logger on destruction
        """
        self.get_logger().info("UI-PUB-WALL || Status: Inactive")

def main(args=None):

    # Initialise rclpy
    rclpy.init(args=args)
    
    # Load node
    node = Pub_Wall()

    # Spin node
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # On keyboard interrupt, shut down the system
        pass
    finally:
        # Log deactivation of node
        node.get_logger().info("UI-SUB-LIDAR || Status: Inactive")

        # Destroy node and shutdown
        node.destroy_node()
        rclpy.shutdown()