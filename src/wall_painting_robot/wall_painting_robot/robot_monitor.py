#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32, Empty, String


class StatusMonitor(Node):
    def __init__(self):
        super().__init__('status_monitor')

        self.odom = None
        self.odomTimestamp = None

        self.battery = None
        self.batteryTimestamp = None

        self.takePictureTimestamp = None
        
        self.ledOn = False
        self.ledTimestamp = None

        self.logs = None
        self.logsTimestamp = None

        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.create_subscription(Float32, '/battery', self.battery_callback, 10)
        self.create_subscription(Empty, '/take_picture', self.take_picture_callback, 10)
        self.create_subscription(Empty, '/led', self.led_callback, 10)
        self.create_subscription(String, '/logs', self.logs_callback, 10)

        # Timer: every 0.5 seconds
        self.create_timer(0.5, self.display_status)

        self.get_logger().info('Waiting for status updates...')

    # -----------------------------
    # Callbacks
    # -----------------------------
    def take_picture_callback(self, _):
        self.takePictureTimestamp = self.get_clock().now()

    def led_callback(self,_):
        # Toggle LED state
        self.ledOn = not self.ledOn

        self.ledTimestamp = self.get_clock().now()



    def logs_callback(self, msg):
        self.logs = msg.data
        self.logsTimestamp = self.get_clock().now()

    def odom_callback(self, msg):
        self.odom = msg
        self.odomTimestamp = self.get_clock().now()

    def battery_callback(self, msg):
        self.battery = msg.data
        self.batteryTimestamp = self.get_clock().now()


    # -----------------------------
    # Helpers
    # -----------------------------
    def ago(self, timestamp):
        if timestamp is None:
            return "unknown"
        
        seconds = (self.get_clock().now() - timestamp).nanoseconds / 1e9
        return "{:.2f} seconds ago".format(seconds)

    # -----------------------------
    # Display
    # -----------------------------
    def display_status(self):

        # Clear the screen and move cursor to top-left
        print("\033[2J\033[H", end="")

        str = "------------------------------------------------------------\nROVER STATUS\n------------------------------------------------------------\n"
        if self.odom is not None:
            pos = self.odom.pose.pose.position
            str += f'Odom Position:\tx={pos.x:.2f}, y={pos.y:.2f}, z={pos.z:.2f} | {self.ago(self.odomTimestamp)}\n'

        if self.battery is not None:
            str += f'Battery:\t{self.battery:.2f} V\t\t\t | {self.ago(self.batteryTimestamp)}\n'

        str += f'LED status:\t{"ON" if self.ledOn else "OFF"}\t\t\t | {self.ago(self.ledTimestamp)}\n'

        if self.logs is not None:
            str += f'Logs:\t\t{self.logs} | {self.ago(self.logsTimestamp)}\n'
        
        if self.takePictureTimestamp is not None:
            str += f'Picture taken {self.ago(self.takePictureTimestamp)}\n'


        print(str, end="", flush=True)

def main(args=None):
    rclpy.init(args=args)
    node = StatusMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

