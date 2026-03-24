
from Nodes.Sub_Camera import Sub_Camera
from Nodes.Sub_Lidar import Sub_Lidar
from Nodes.Sub_Force import Sub_ManiForce
from Nodes.Pub_Wall import Pub_Wall

import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String

import threading

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
            if self.logger == 0: self.logger = subscribers[sub_key].getLogger()
        
        # Spin nodes on a separate thread
        # A separate thread is required as spinning is a infinite looped execution
        self.daemon_thread = threading.Thread(target=self._SpinNodes(),daemon=True)
        self.daemon_thread.start()


    def _SpinNodes(self):

        if self.spun:
            if (self.logger != 0): self.logger.info("UI-NODE-HANDLER || Nodes have been previously spun")
        else:

            if (self.logger != 0): self.logger.info("UI-NODE-HANDLER || Spinning all subscribers and publishers")

            # Intialise rlcpy
            rclpy.init()

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
    
    def CallbackLidar(self,data):
        pass

    def CallbackCamera(self,data):
        pass

    def CallbackManiForce(self,data):
        pass

    def Publish(self,publisher_id,msg):
        self.publishers[publisher_id].Publish(msg)



def main(args=None):

    # Initialise rclpy
    rclpy.init(args=args)
    
    # Load Publishers
    publishers = {}
    publishers['Wall'] = Pub_Wall()

    # Load Subscribers
    subscribers = {}
    subscribers['Camera'] = Sub_Camera()
    subscribers['Lidar'] = Sub_Lidar()
    subscribers['ManiForce'] = Sub_ManiForce()

    handler = NodeHandler(publishers,subscribers)

    # Return handler if called from somewhere else (In other words, GUI.py)
    if __name__ != '__main__': return handler