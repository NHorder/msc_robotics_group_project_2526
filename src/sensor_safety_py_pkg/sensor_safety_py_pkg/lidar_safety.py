################################
# lidar_safety.py
# Part of the sensor_safety_py_pkg
#
# Author: Nathan Horder (nathan.horder.700@cranfield.ac.uk)
# Part of Cranfield University MSC Robotics Group Project 2025-2026
################################
#%%
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import threading
from std_msgs.msg import String
import json
from enum import Enum


############
# DEV NOTE:
# This will not be active during simulation execution due to use of LiDAR.
# If used in real-world, multi-LiDAR fusion is required to ensure 360 unobstructed
# view of environment, with assumed ignore of objects ON the mobile base
# current simulation does not do this
############

"""
SafetyCommands
Enum class (Custom type) to hold possible safety related commands, Continue: No issues, Slow: Slow the robots movements, Terminate: Cease all action immediately
"""
class SafetyCommands(Enum):
    CONTINUE = 1
    SLOW = 2
    TERMINATE = 3

"""
LidarSafety
Class to ensure system slows or stops when entities are within a certain distance of the mobile base through 2D LiDAR
"""
class LidarSafety(Node):

    def __init__(self):
        """
        Initialisation Method - Prepares class for execution
        """
        super().__init__('safety_lidar')

        # Open the JSON settings file and read the data
        with open("settings.json","r") as file:
            self.settings = json.load(file)
        file.close()

        # Create the subscriber directly to the lidar readings
        self.subscriber = self.create_subscription(LaserScan,'/scan',self._Process,10)

        # Create publisher for safety publishing - motion systems should subscribe to this, and upon reading anything but 'Continue' should act
        self.publisher = self.create_publisher(String,'safety',10)

        # Need direct link to UI (for reset)

        # Store functions
        self.safety_funcs = [self._TerminateMovingEntity,self._TerminateAllEntities]

        self.action_taken = SafetyCommands.CONTINUE

        self.thread_results = []

    def _Process(self,msg):
        self.thread_results.clear()
        # Called when scan data is received

        # Loop through all safety functions and start each on a thread
        for func in self.safety_funcs:
            thread = threading.Thread(target=func,args=(msg),daemon=True)
            thread.start()

        ##########
        # Dev Note:
        # Knowledge of multi-threading and thread-safety is limited, ideally, each thread upon identifying a termination condition
        # will immediately publish instead of waiting for next LiDAR scan.
        ##########

        # Publish whenever a new lidar scan is given. 
        self._Publish()

    def _Reset(self):
        # Set action taken to 
        self.action_taken = SafetyCommands.CONTINUE

        # Notify caller that a RESET has occurred
        return True
    
    def _TerminateAllEntities(self,msg):
        # Immediately end action if termination command has been issued
        if self.action_taken == SafetyCommands.TERMINATE:
            return

        # Loop through all ranges, if a range is less than the allowed terminate distance, then issue a termination command
        for range in msg.ranges:
            if range <= float(self.settings['terminate_distance']):
                # Update state
                self.thread_results.append(SafetyCommands.TERMINATE)

                # End loop, no point in continuing, a termination command has been issued
                break

    def _TerminateMovingEntity(self,msg):

        # Immediately end action if termination command has been issued
        if self.action_taken == SafetyCommands.TERMINATE:
            return
        

        entities = [] # Replace with check / function to call to check for moving entities

        abrupt_end = False
        slow = False
        
        # Check if moving entities
        for entity in entities:

            # If within termination distance, terminate
            if entity.range <= float(self.settings['']):
                self.thread_results.append(SafetyCommands.TERMINATE)
                abrupt_end = True
                break

            # If within slow distance and the entity is moving towards the robot or will enter termination distance, set command to slow
            # When an entity's sproject path intersects with the robots termination distance, it is assumed their goal is the robot.
            elif entity.range <= float(self.settings['slow_distance_moving_entity'] and entity.goal == 'Robot'):
                self.thread_results.append(SafetyCommands.SLOW)
                slow = True
        
        # If slow has been issued, add result to slow down cause
        if slow:
            self.thread_results.append(SafetyCommands.SLOW)

        # If loop was not abruptly ended, and the current action is Continue, append continue
        elif (not abrupt_end) and (self.action_taken == SafetyCommands.CONTINUE):
            self.thread_results.append(SafetyCommands.CONTINUE)

    def _Publish(self):
        msg = String()

        # Loop through all resuslts, note this function is also called on the threads
        for result in self.thread_results:

            # IF any result is terminate, break loop, set termination to true
            if result == SafetyCommands.TERMINATE: 
                self.action_taken = SafetyCommands.TERMINATE
                break

            # IF the result is SLOW, then set action taken to slow, keeping going through loop in case of a termination
            elif result == SafetyCommands.SLOW:
                self.action_taken = SafetyCommands.SLOW

            # IF the current action taken is NOT slow, then it's continue
            elif self.action_taken != SafetyCommands.SLOW:
                self.action_taken = SafetyCommands.CONTINUE


        if self.action_taken == SafetyCommands.TERMINATE:
            msg.data = 'terminate'
        elif self.action_taken == SafetyCommands.SLOW:
            msg.data = 'slow'
        else:
            msg.data = 'continue'

        self.publisher.publish(msg)
        


def main(args=None):
    return # Prevention of spinning, due to simulation representation, remove when simulation meets requirements.

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
