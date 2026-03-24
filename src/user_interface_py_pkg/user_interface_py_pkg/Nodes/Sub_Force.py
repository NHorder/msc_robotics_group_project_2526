
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from NodeHandler import NodeHandler

class Sub_ManiForce(Node):
    """
    Class: Sub_ManiForce
    Purpose: ROS2 Manipulator Force node, retrieves information from ROS2 manipulator force publishers
    Preferable Links: Link to available NodeHandler, allows connection to UI
    """
    
    def __init__(self):
        """
        Initialisation Method

        Starts subscription service and notifies user of when active
        """

        super().__init__('ui/sub/maniforce')

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
        self.get_logger().info("UI-SUB-MANIFORCE || Status: Active")

    def callback(self,msg):
        """
        Callback Method

        Called upon receiving ROS2 updates from a publisher on the same topic
        Notifies operator of update, if handler is present, notify it to update information
        """
        self.get_logger().info(f"UI-SUB-MANIFORCE // Retrieved: {msg.data}")
        self.data = msg

        # If handler is present, pass data to it
        if self.handler != 0: self.handler.CallbackManiForce(msg.data)

    def NotifyDestruction(self):
        """
        Method to display logging when node is about to be destroyed
        """
        self.get_logger().info("UI-SUB-MANIFORCE|| Status: Inactive")

    def SetHandler(self,handler: NodeHandler):
        """
        Method to attach handler
        """
        self.handler = handler
    

def main(args=None):

    # Initialise rclpy
    rclpy.init(args=args)
    
    # Load node
    node = Sub_ManiForce()

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