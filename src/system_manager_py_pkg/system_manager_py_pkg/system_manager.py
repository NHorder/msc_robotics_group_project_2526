################################
# system_manager.py
# Part of the system_manager_py_pkg
#
# Part of Cranfield University MSC Robotics Group Project 2025-2026
################################

# Imports!
import rclpy
from rclpy.node import Node
from enum import Enum
from std_msgs.msg import String

# Enumerator class for custom states
# STANDBY: Robot awaiting instructions from user interface
# PLANNING: Robot receiving motion paths or preparing motion paths
# MOVING_MB: Motion of the robot's Mobile Base
# MOVING_MA: Motion of the robot's Manipulator Arm
# TERMINATE: Terminate all motion immediately, wait until specific message before returning to standby
# NOTE: As implied, Mobile Base and Manipulator Arm cannot be moving simultaneously 

# NORMAL and REDUCED are movement states
class States(Enum):
    STANDBY = 1
    PLANNING = 2
    MOVING_MB = 3
    MOVING_MA = 4
    TERMINATE = 5

    NORMAL = 6
    REDUCED = 7

"""
Class to handle robot states and transitions between states
"""
class System_Manager(Node):
    

    def __init__(self):
        """
        Initialisation Method
        """

        # Required variable due to setup of nodes
        # Each subscription will initially fire once, causing potential issues on setup
        self.initialising = True

        # Define current state and previous state
        self.current_state = States.STANDBY
        self.previous_state = None

        self.motion_state = States.NORMAL

        # Establish subscribers
        self.nodes = {}
        self.nodes["imu"] = self.create_subscription(String,'/imu',lambda msg: self._SubscriberCallback(msg, 'imu'))
        self.nodes["wheel_odom"] = self.create_subscription(String,'/wheel_odom',lambda msg: self._SubscriberCallback(msg, 'wheel_odom'))
        self.nodes['gui'] = self.create_subscription(String,'/gui/action',lambda msg: self._SubscriberCallback(msg, 'GUI'))

        # Establish critical node - for critical information calls
        self.critical_node = self.create_subscription(String,'/critical',self._CriticalCallback)

        # Save node_details to determine current state - Key: Boolean  (Node: IsMoving(bool))
        self.node_msg = {}

        self.initialising = False

        # Create publsiher
        self.publisher = self.create_publisher(
            String,
            '/system_state',
            10
        )

        # Periodically determine state and publish
        # NOTE: Safety is critical, dedicated bypass of state determination
        self.timer = self.create_timer(0.5, self._DetermineState)

    

    def _SubscriberCallback(self,msg,topic_key):
        """
        Callback method for each subscriber, saves message under topic
        """

        # Don't process information if initialising
        if self.initialising:
            return
        
        match topic_key:

            case "gui": # Task: Moving base, moving arm, etc.
                pass

            case "imu": # Raw movement readings
                # Process data to determine if movement is detected
                pass

            case "wheel_dom":
                pass

            case "manipulator_arm": # Raw arm movement readings
                # Process data to determine if movement is detected
                pass

            case _:  # Default Case
                pass

    def _CriticalCallback(self,msg):
        """
        Dedicated Bypass method for state determination - occurs immediatly upon receiving message
        """
        
        # If any message is "TERMINATE", terminate immediately
        if msg == 'TERMINATE':
            self.current_state = States.TERMINATE
        elif msg == 'REDUCE':
            # If message is reduce, set motion state to reduced (Slower movement speeds)
            self.motion_state = States.REDUCED
        else:
            # Reset to standby and normal movement
            self.current_state = States.STANDBY
            self.motion_state = States.NORMAL
        
        # Publish information
        self._Publish()

    def _DetermineState(self):
        """
        Method to determine state based on available information
        """


        self._Publish()

    def _Publish(self):
        """
        Method to publish information to /system_state
        """
        ## Publish current state (to be read by GUI) 

        # Define message
        msg = String()

        if self.motion_state == States.NORMAL: txt = ""
        else: txt = " (Reduced)"

        # Fill message data with string information (primarily for GUI)
        if self.current_state == States.STANDBY:
            msg.data = 'On Standby'

        elif self.current_state == States.PLANNING:
            msg.data = 'Planning Motion Paths'

        elif self.current_state == States.MOVING_MB:
            msg.data = 'Mobile Base In Motion' + txt

        elif self.current_state == States.MOVING_MA:
            msg.data = 'Manipulator Arm in Motion' + txt

        elif self.current_state == States.TERMINATE:
            msg.data = 'Terminate Command Issued'

        else:
            # Error log
            msg.data = 'Unknown'
            # Publish to critical topic of termination due to unknown state

        # Publish the message to /system_state
        self.publisher.publish(msg)

