################################
# sub_lidar.py
# Part of the user_interface_py_pkg/nodes
#
# Part of Cranfield University MSC Robotics Group Project 2025-2026
################################

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Sub_Lidar(Node):
    """
    Class: Sub_Lidar
    Purpose: ROS2 LiDAR node, retrieves information from ROS2 LiDAR publishers
    Preferable Links: Link to available NodeHandler, allows connection to UI
    """
    
    def __init__(self):
        """
        Initialisation Method

        Starts subscription service and notifies user of when active
        """

        super().__init__('ui/sub/lidar')

        # Create subscription to LiDAR ROS 2 topic
        self.subscription = self.create_subscription(
            String,
            '',
            self.callback,
            10
        )
        # Suppress warning
        self.subscription

        # Prepare Handler
        self.handler = 0

        # Log activation of node
        self.get_logger().info("UI-SUB-LIDAR || Status: Active")

    def callback(self,msg):
        """
        Callback Method

        Called upon receiving ROS2 updates from a publisher on the same topic
        Notifies operator of update, if handler is present, notify it to update information
        """
        self.get_logger().info(f"UI-PUB-WALL // Retrieved: {msg.data}")
        self.data = msg

        # If handler is present, pass data to it
        if self.handler != 0: self.handler.NotifyHandler("Lidar",msg.data)

    def NotifyDestruction(self):
        """
        Method to display logging when node is about to be destroyed
        """
        self.get_logger().info("UI-SUB-LIDAR || Status: Inactive")

    def SetHandler(self,handler):
        """
        Method to attach handler
        """
        self.handler = handler
    

def main(args=None):

    # Initialise rclpy
    rclpy.init(args=args)
    
    # Load node
    node = Sub_Lidar()

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