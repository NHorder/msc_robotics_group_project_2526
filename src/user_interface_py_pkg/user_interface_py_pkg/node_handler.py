################################
# node_handler.py
# Part of the user_interface_py_pkg
#
# Part of Cranfield University MSC Robotics Group Project 2025-2026
################################

from nodes.sub_camera import Sub_Camera
from nodes.sub_lidar import Sub_Lidar
from nodes.sub_force import Sub_ManiForce
from nodes.pub_wall import Pub_Wall

import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String
import asyncio
import threading
import numpy as np
from holoviews.streams import Pipe

class NodeHandler():
    """
    Class: NodeHandler
    Purpose: Handles information transfer between UI and nodes

    Core variables:
    - publishers: Dict of publisher classes
    - subscribers: Dict of subscriber classes
    - subscriber_data: Dict of subscriber data (to display)

    """
    
    def __init__(self,publishers,subscribers):
        """
        Initialisation Method
        """

        # Save link to publishers and subscribers locally
        self.publishers = publishers
        self.subscribers = subscribers

        # Subscriber data - what the UI will link to
        # I.e callback lidar is triggered, subscriber data is updated, UI reads subscriber data and updates UI
        self.subscriber_data = {}

        self.spun = False
        self.logger = 0

        # Set handler to all subscribers (Resulting in callbacks)
        for sub_key in self.subscribers.keys():
            subscribers[sub_key].SetHandler(self)

            # Set empty list for subscriber data - means each key has an empty list item (for later updates)
            self.subscriber_data[sub_key] = []

            # Set logger to that of first subscriber node to enable logging
            #if self.logger == 0: self.logger = subscribers[sub_key].getLogger()

        print("Hi?")

        # Spin nodes on a separate thread
        # A separate thread is required as spinning is a infinite looped execution
        self.daemon_thread = threading.Thread(target=self._SpinNodes,daemon=True)
        self.daemon_thread.start()

        print("Hello?")

    def _SpinNodes(self):
        """
        Method handles spinning of all subscribers and publishers on a daemon thread
        - Must be executed on a daemon thread, as spinning will block futher actions
        """

        if self.spun:
            if (self.logger != 0): self.logger.info("UI-NODE-HANDLER || Nodes have been previously spun")
        else:

            if (self.logger != 0): self.logger.info("UI-NODE-HANDLER || Spinning all subscribers and publishers")

            # Create a mutli-thread executor
            # Required to spin multiple nodes - spinning normally would result in one node spun, other nodes not spun
            exe = MultiThreadedExecutor()

            # Loop through all publishers, add to exe
            for pub_key in self.publishers.keys():
                exe.add_node(self.publishers[pub_key])
            
            # Loop through all subscribers, add to exe
            for sub_key in self.subscribers.keys():
                exe.add_node(self.subscribers[sub_key])

            # Spin exe
            try:
                exe.spin()

            except KeyboardInterrupt:
                # On keyboard interrupt, shut down the system
                pass

            finally:

                # Destroy all publishers
                for pub_key in self.publishers.keys():
                    self.publishers[pub_key].NotifyDestruction()
                    self.publishers[pub_key].destroy_node()

                # Destroy all subscribers
                for sub_key in self.subscribers.keys():
                    self.subscribers[sub_key].NotifyDestruction()
                    self.subscribers[sub_key].destroy_node()
                
                # Shutdown rclpy
                rclpy.shutdown()
    
    def NotifyHandler(self,subscriber_id,data):
        """
        Subscriber link method, called by subscribers on update
        Updates local data, throws warning if unknown subscriber notifies
        """
        if (subscriber_id in self.subscriber_data.keys()):

            if (subscriber_id == "Lidar"):
                point_data = Process_Lidar(data)
                self.subscriber_data["Lidar"] = point_data


            else:
                self.subscriber_data[subscriber_id] = data

        elif self.logger != 0:
            self.logger.warning("UI-NODE-HANDLER || Unknown subscriber notifying handler")


    async def GetData(self,subscriber_id:String,gui_pipe:Pipe):
        while True:
            await asyncio.sleep(1)
            gui_pipe.send(np.array(self.subscriber_data[subscriber_id]))

    def Publish(self,publisher_id,msg):
        """
        Method to publish information through a publisher
        """
        self.publishers[publisher_id].Publish(msg)

    def LoadFakeData(self):

        # Camera and Manipulator Arm Plans are linked, Camera takes a still shot, path is planned using dots on the image
        # Camera is just an image btw - path is points plotted on top of it ()
        self.subscriber_data['Camera'] = "./camera/still.jpg"
        self.subscriber_data['ManipulatorArmPlan'] = "./camera/still_arm_path.jpg"
        
        self.subscriber_data['RobotInformation']

        self.subscriber_data['WorldInfo'] = {"Temperature":12}

        self.subscriber_data['EntitiesNearby'] = {1:"3m",2:"5m",3:"6m"}



def Process_Lidar(dat):
    header = dat.header
    range = dat.ranges
    angle_min = dat.angle_min
    angle_max = dat.angle_max
    angle_increment  = dat.angle_increment
    range_min = dat.range_min
    range_max = dat.range_max

    points = []
    current_angle = angle_min
    i = 0
    group_x = []
    group_y = []

    for range_val in range:

        group_x.append(range_val * np.cos(current_angle))
        group_y.append(range_val * np.sin(current_angle))

        if True:#(i % 5 == 0):
            points.append((np.mean(group_x),np.mean(group_y)))
            group_x.clear()
            group_y.clear()

        current_angle+=angle_increment
        i+=1
    

    
    return points



def main(args=None):
    """
    Main function used to start the handler
    Returns handler object if not executed directly
    """
    # Intialise rlcpy
    rclpy.init()
    
    # Load Publishers
    publishers = {}
    #publishers['Wall'] = Pub_Wall()

    # Load Subscribers
    subscribers = {}
    subscribers['Camera'] = Sub_Camera()
    subscribers['Lidar'] = Sub_Lidar()
    #subscribers['ManiForce'] = Sub_ManiForce()

    handler = NodeHandler(publishers,subscribers)

    # Return handler if called from somewhere else (In other words, GUI.py)
    if __name__ != '__main__': return handler
