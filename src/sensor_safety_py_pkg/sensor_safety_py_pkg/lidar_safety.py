################################
# lidar_safety.py
# Part of the sensor_safety_py_pkg
#
# Author: Nathan Horder (nathan.horder.700@cranfield.ac.uk)
# Part of Cranfield University MSC Robotics Group Project 2025-2026
################################
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import numpy as np
from std_msgs.msg import String, Bool
import json


"""
LidarSafety
Class to ensure system slows or stops when entities are within a certain distance of the mobile base through 2D LiDAR
"""
class LidarSafety(Node):

    def __init__(self):
        """
        Initialisation Method - Prepares class for execution
        """
        super().__init__('system_health_manager')
        pass



def main(args=None):
    rclpy.init(args=args)
    
    # Load node
    node = LidarSafety()

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

if __name__ == '__main__':
    main()