################################
# system_health_manager.py
# Part of the system_manager_py_pkg
#
# Author: Nathan Horder (nathan.horder.700@cranfield.ac.uk)
# Part of Cranfield University MSC Robotics Group Project 2025-2026
################################

# Imports!
import rclpy
from rclpy.node import Node
from enum import Enum
from std_msgs.msg import String
from diagnostic_msgs.msg import DiagnosticStatus,DiagnosticArray
import numpy as np


"""
Enumerator Class for custom type Node Status - Based on difference between last message and new message (using a rolling mean and standard deviation)
HEALTHY: Indicates node is functioning correctly
NO_CONNECTION: Node has not published information since initialisation
ANOMALOUS: Node has encountered unexpected delays in publishing
FAULTY: Node has repeatedly encounted unexpeccted delays in publishing  - terminate system, something is most likely wrong
"""
class Node_Status(Enum):
    HEALTHY = 1
    NO_CONNECTION = 2
    ANOMALOUS = 3
    FAULTY = 4


"""
SystemHealthManager
Class used to determine health of the system.

This is achieved by subcribing to core nodes and ensuring they are publishing, 
then combining them into systems for generalised system health
"""
class SystemHealthManager(Node):

    def __init__(self):
        """
        Initialisation Method - Prepares class for execution
        """
        super().__init__('system_health_manager')

        # Initial variables
        self.initialising = True
        self.fault_tolerance = 10
        self.prev_info = {}
        self.publisher = self.create_publisher(
           DiagnosticArray,
           '/system_health',
           10
        )

        #NOTE: This does not account for health of the data - that's at sensor processing level

        # Health of nodes: Starts with no-connection, can be: HEALTHY, NO_CONNECTION, ANOMALOUS, FAULTY
        # ANOMALOUS means a unexpected increase in timing between messages
        # FAULTY: Repeated unexpected increase in timing between messages
        # NO_CONNECTION: Default value at startup
        self.node_status = {}
        self.node_status["camera"] = Node_Status.NO_CONNECTION
        self.node_status["lidar"] = Node_Status.NO_CONNECTION
        self.node_status["imu"] = Node_Status.NO_CONNECTION
        self.node_status["odom"] = Node_Status.NO_CONNECTION
        self.node_status['gui'] = Node_Status.NO_CONNECTION
        self.node_status['clock'] = Node_Status.NO_CONNECTION

        # Health of systems
        self.systems_status = {}
        self.systems_status['GUI'] = [DiagnosticStatus.STALE,'NO_CONNECTION']
        self.systems_status['Mobile_Base'] = [DiagnosticStatus.STALE,'NO_CONNECTION']
        self.systems_status['Manipulator_Arm'] = [DiagnosticStatus.STALE,'NO_CONNECTION']
        self.systems_status['Visual_Sensor_Systems'] = [DiagnosticStatus.STALE,'NO_CONNECTION']
        self.systems_status['DataProcessing'] = [DiagnosticStatus.STALE,'NO_CONNECTION']
        self.systems_status['Path_Planning'] = [DiagnosticStatus.STALE,'NO_CONNECTION']
        self.systems_status['Path_Following'] = [DiagnosticStatus.STALE,'NO_CONNECTION']
        self.systems_status['Simulation'] = [DiagnosticStatus.STALE,'NO_CONNECTION']

        # Creation of subscribers
        # ## Not done yet, need more, awaiting completion of other modules 
        self.nodes = {}
        self.nodes['clock']= self.create_subscription(String,'/clock',lambda msg: self._NodeHealth(msg, 'clock'),10)

        self.nodes["camera"] = self.create_subscription(String,'/camera/image_raw',lambda msg: self._NodeHealth(msg, 'camera'),10)
        self.nodes["lidar"]  = self.create_subscription(String,'/scan',lambda msg: self._NodeHealth(msg, 'lidar'),10)
        self.nodes["imu"] = self.create_subscription(String,'/imu',lambda msg: self._NodeHealth(msg, 'imu'),10)
        self.nodes["odom"] = self.create_subscription(String,'/wheel_odom',lambda msg: self._NodeHealth(msg, 'odom'),10)
        self.nodes["gui"] = self.create_subscription(String,'/gui/actions',lambda msg: self._NodeHealth(msg, 'gui'),10)

        # Periodically run SystemHealth checks
        self.timer = self.create_timer(0.5, self._SystemHealth)
        
        # Disable intialising
        self.initialising = False

        self.get_logger().info("System-Health-Manager: Running!")

    def _NodeHealth(self,msg,topic_key):
        """
        _NodeHealth (Private)
        Subscriber callback method to check node health - achieved through a rolling mean and standard deviation
        NOTE: If a node is ANOMALOUS or FAULTY, it will NOT update the mean or std that loop to avoid inconsistencies

        Arguments:
            - <variable_type> : msg || Inbound ROS2 message
            - str: topic-key || Name of Node whose health is being checked

        Returns: N/A
        """
        
        # Due to setup, this is required, as all nodes will publish a message immedately on load
        # resulting in errors due to empty messages
        if self.initialising:
            return

        # IF the node is faulty, immediately throw errors and terminate current sequence
        if self._NodeHealth[topic_key] == Node_Status.FAULTY:
            # Throw errors and notifications
            # Terminate current sequence     
            return
        
        # Collect the msg time in sec and nanosec - both are required due to ROS 2 publishing speeds
        timestamp = msg.header.stamp
        time = timestamp.sec + timestamp.nanosec / 1e9

        # Try to access the data - data may not be present at intial run
        try:
            previous_time = self.node_prev[topic_key][0]
            mean = self.node_prev[topic_key][1]
            std = self.node_prev[topic_key][2]
            num_seen = self.node_prev[topic_key][2]
            anomalous_readings = self.node_prev[topic_key][3]
        
        # Else add it to the dictionary as the first item
        except:
            # Add it to the dictionary - if it's not already present
            # Time = time, mean = time, std = 0, num_seen = 1
            self.node_prev[topic_key] = [time,time,0.5,1]

            # Terminate as it's the first run
            return
        
        # Determine difference in time
        delta_time = time - previous_time

        # Determine if within range of mean and +3 stds
        if (delta_time > mean+(3 * std)):

            # If the new time difference exceeds known values signficantly, then it's anomalous
            # Essentially marking it for something to keep an eye on
            self._NodeHealth[topic_key] = Node_Status.ANOMALOUS
            anomalous_readings +=  1
            # Send warning notification

            # If it's presented over fault_tolerance readings, then it's faulty.
            if anomalous_readings > self.fault_tolerance:
                self._NodeHealth[topic_key] = Node_Status.FAULTY
                # Notify of fault
                # Make request to slow down actions

            # NOTE: anomalous_readings is NOT RESET, as if it faults a number of times, something is wrong. It should not be ignored
            #       hence, if it occurs often, it will be noticed faster

            # Update anomalous reading count - values not updated due to being anomalous, but anomalous counter is needed to achieve FAULTY node status
            self.node_prev[topic_key][3] = anomalous_readings

            # Return: Does not affect mean or std, given it's anomalous nature - it'll squew results otherwise
            return

        # Else it's fine
        else:
            self.node_status[topic_key] = Node_Status.HEALTHY

        # Update mean
        delta_mean = delta_time - mean 
        mean_new = mean + (delta_mean / num_seen)
        
        # Update std
        sum_squares = sum_squares + delta_mean*(delta_time-mean_new)
        var = sum_squares / num_seen 
        std_new = np.sqrt(var)

        # Update node
        self.node_prev[topic_key] = [time,mean_new,std_new,num_seen+1,anomalous_readings]
    
    def _SystemHealth(self):
        """
        _SystemHealth (Private)
        Method called periodically to check system health - Calls each system with their respective nodes

        Arguments: N/A

        Returns: N/A
        """
        # Update GUI status - solely based on GUI node
        self._SystemHealthCheck('GUI',['gui'])

        ## Mobile Base 
        self._SystemHealthCheck('Mobile_Base',['imu','odom'])

        ## Manipualtor Arm
        #self._SystemHealthCheck('Manipulator_Arm') # All nodes of manipulator arm, input and output

        ## Visual Sensor Systems (Lidar, camera, etc)
        self._SystemHealthCheck('Visual_Sensor_Systems',['camera','lidar']) # And any other sensors

        ## Data Processing (package)
        self._SystemHealthCheck('DataProcessing',['camera','lidar']) # And processed output nodes

        ## Path Planning (package)
        #self._SystemHealthCheck('Path_Planning') # Base planning and manipulator arm following

        ## Path Following (package)
        #self._SystemHealthCheck('Path_Following') # base following and manipualtor arm following

        ## Simulation (package) - 'clock' is used as it's automatically created alongside the simulation
        self._SystemHealthCheck('Simulation',['clock'])

        # Publish results
        self._Publish()

    def _SystemHealthCheck(self,system,nodes):
        """
        _SystemHealthCheck (Private)
        Method to check system health, and prepares publishing information

        Arguments:
            - str : system || Identification of system being checked
            - list : nodes || List of all subscriber nodes of this class

        Returns: N/A
        """

        # Init counters
        health = 0
        anom = 0
        offline = 0
        num_nodes = len(nodes)


        # Loop through each node related to the system, and collect status
        for node in nodes:
            if self.node_status[node] == Node_Status.HEALTHY: health+=1
            elif self.node_status[node] == Node_Status.NO_CONNECTION: offline+1
            elif self.node_status[node] == Node_Status.ANOMALOUS: anom += 1
            else:
                # If ANY node is Faulty, throw an immediate faulty error - it should not be acting
                # All further actions should be blocked - and to stop the subscriber. 
                self.systems_status[system] = Node_Status.FAULTY
                # Throw immediate faulty error
                return

        # If all nodes are healthy, then the system is healthy
        if num_nodes == health:
            self.systems_status[system] = [DiagnosticStatus.OK,'HEALTHY']

        # If all nodes haven't sent any messages (Meaning no status change), then it's offline
        # This is a warning, as it should be active once the system begins running. If it's not it's probably an issue
        elif num_nodes == offline:
            self.systems_status[system] = [DiagnosticStatus.WARN,'NO-CONNECTION']

        # If less than 25% of the nodes are anomlous, maintain system, mark as anomalous
        elif (offline != 0) or (anom / num_nodes) <= 0.25:
            # Notify issue
            self.systems_status[system] = [DiagnosticStatus.WARN,'ANOMALOUS']
        
        # Otherwise, more than 25% of nodes are reporting anomalous at the SAME TIME, mark as faulty, begin shutdown procedures
        else:
            # Update system to show faulty state
            self.systems_status[system] = [DiagnosticStatus.ERROR,'FATAL']

            # By setting the last node accessed to FAULTY, it will automatically re-trigger the fault detection next loop
            self.node_status[node] = Node_Status.FAULTY

            # Send intruction to terminate and block further mobile base commands
            # Send notification of faulty node
              
    def _Publish(self):
        """
        _Publish (Private)
        Method to publish system health message

        Arguments: N/A

        Returns: N/A
        """
        # Prepare msg
        msg = DiagnosticArray()

        # Loop through all system statuses, collect their information and add to message
        for system in self.systems_status.keys():

            # Collect pre-prepared array [Status, Message]
            status = self.systems_status[system]

            item = DiagnosticStatus()
            item.name = system
            item.level = status[0]
            item.message = status[1]
            msg.status.append(item)

        # Publish
        self.publisher.publish(msg)


def main(args=None):
    """
    main
    Function to spin System_Health_Manager nodes
    """
    rclpy.init(args=args)
    
    # Load node
    node = SystemHealthManager()

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