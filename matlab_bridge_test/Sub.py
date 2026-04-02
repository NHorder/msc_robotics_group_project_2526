#!/usr/bin/env python3
"""
Publisher Node Example - Waiter

This node publishes order messages to the 'orders' topic.
It simulates a restaurant waiter announcing customer orders.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import socket
import threading

HOST = '0.0.0.0'
PORT = 5001


class MatLabSub(Node):
    """Publisher node that announces orders to the kitchen."""

    def __init__(self):
        super().__init__('waiter')
        
        # Create a publisher that will send String messages to the 'orders' topic
        # Queue size of 10 means we can buffer up to 10 messages
        self.publisher = self.create_publisher(
            String,      # Message type
            'orders',    # Topic name
            10           # Queue size
        )
        
        # Create a timer that calls publish_order every 1.0 second
        self.timer = self.create_timer(1.0, self.publish_order)
        self.order_count = 0
        
        self.get_logger().info('Waiter node started!')



        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.bind((HOST,PORT))
        self.sock.listen(1)
        print(f"Waiting for MATLAB to connect to port {PORT}")
        self.conn,addr = self.sock.accept()
        print(f"MATLAB connected from {addr}")

        threading.Thread(target=self.receive_loop,daemon=True).start()
    
    def publish_order(self):
        """Callback function called by the timer to publish an order."""
        # Create a String message
        msg = String()
        self.order_count += 1
        msg.data = f'Order #{self.order_count}: Burger'
        
        # Publish the message to the 'orders' topic
        self.publisher.publish(msg)
        
        # Log the action (visible in terminal)
        self.get_logger().info(f'Announcing: {msg.data}')

    def receive_loop(self):
        while True:
            data = self.conn.recv(1024)
            if not data:
                continue
            
            msg_str = data.decode().strip()

            if msg_str:
                print(msg_str)

def main(args=None):
    """Main function to initialize and run the waiter node."""
    # Initialize ROS2
    rclpy.init(args=args)
    
    # Create the node
    node = MatLabSub()
    
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
