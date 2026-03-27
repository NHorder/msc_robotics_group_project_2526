import rclpy
from rclpy.node import Node
from enum import Enum
from std_msgs.msg import String

class States(Enum):
    STANDBY = 1
    PLANNING = 2
    MOVING_MB = 3
    MOVING_MA = 4


class System_Manager(Node):
    
    def __init__(self):

        self.initialising = True

        self.current_state = States.STANDBY
        self.previous_state = None

        # All subscriber nodes, 
        self.nodes = {}
        self.nodes["imu"] = self.create_subscription(String,'/imu',lambda msg: self._SubscriberCallback(msg, '/imu'))
        self.nodes["wheel_odom"] = self.create_subscription(String,'/imu',lambda msg: self._SubscriberCallback(msg, '/wheel_odom'))
        self.nodes['gui'] = self.create_subscription(String,'gui/action',lambda msg: self._SubscriberCallback(msg, 'GUI'))


        self.previous_msg = {}

        self.initialising = False

        self.publisher = self.create_publisher(
            String,
            '/system_state',
            10
        )

        # Need to set up a timer for publishing
    

    def _SubscriberCallback(self,msg,topic_key):

        # Don't process information if initialising
        if self.initialising:
            return
        
        match topic_key:

            case "gui": # Task: Moving base, moving arm, etc.
                pass

            case "imu": # Raw movement readings
                # Process data to determine if movement is detected, compare to current state
                pass

            case "wheel_dom":
                pass

            case "manipulator_arm": # Raw arm movement readings
                # Process data to determine if movement is detected, compare to current state
                pass

            case _:  # Default Case
                pass

    def _Publish(self):
        ## Publish current state (to be read by GUI) 

        # Define message
        msg = String()

        # Fill message data with string information (primarily for GUI)
        if self.current_state == States.STANDBY:
            msg.data = 'On Standby'

        elif self.current_state == States.PLANNING:
            msg.data = 'Planning Motion Paths'

        elif self.current_state == States.MOVING_MB:
            msg.data = 'Mobile Base In Motion'

        elif self.current_state == States.MOVING_MA:
            msg.data = 'Manipulator Arm in Motion'

        else:
            # Error log
            msg.data = 'Unknown'

        # Publish the message to /system_state
        self.publisher.publish(msg)

