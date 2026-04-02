#!/usr/bin/env python3
"""
Subscriber Node Example - Chef

This node subscribes to the 'orders' topic and processes incoming orders.
It simulates a restaurant chef receiving and preparing orders.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import socket

HOST = '0.0.0.0'
PORT = 5000


class ChefNode(Node):
    """Subscriber node that listens for and processes orders."""

    def __init__(self):
        super().__init__('chef')
        
        # Create a subscription to listen to messages on the 'orders' topic
        # Queue size of 10 means we can buffer up to 10 messages
        self.subscription = self.create_subscription(
            String,               # Message type
            'orders',             # Topic name
            self.order_callback,  # Callback function when message arrives
            10                    # Queue size
        )
        
        # Suppress unused variable warning
        self.subscription  # noqa: F841
        
        self.get_logger().info('Chef node started! Listening for orders...')


        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.bind((HOST,PORT))
        self.sock.listen(1)
        print(f"Waiting for MATLAB to connect on port {PORT}")
        self.conn,addr = self.sock.accept()
        print(f"MATLAB connected from {addr}")
    
    def order_callback(self, msg):
        """Callback function that is called whenever a message arrives on the topic.
        
        Args:
            msg: The received message (String)
        """
        # Log the received order
        self.get_logger().info(f'Received order: {msg.data}')
        
        # Simulate cooking
        self.get_logger().info('Starting to cook...')

        try:
            self.conn.sendall((msg.data + "\n").encode())
        except BrokenPipeError:
            print("MATLAB Disconnected")
            self.conn.close()


def main(args=None):
    """Main function to initialize and run the chef node."""
    # Initialize ROS2
    rclpy.init(args=args)
    
    # Create the node
    node = ChefNode()
    
    try:
        # Keep the node running and processing callbacks
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Allow graceful shutdown with Ctrl+C
        pass
    finally:
        # Clean up
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
