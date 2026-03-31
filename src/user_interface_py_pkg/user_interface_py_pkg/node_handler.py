import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String
import asyncio
import threading
import numpy as np
from holoviews.streams import Pipe
from diagnostic_msgs.msg import DiagnosticArray
from sensor_msgs.msg import LaserScan, Image


class NodeHandler(Node):
    
    def __init__(self):

        super().__init__('gui_node_handler')
        self.decoder = Decoder()

        self.subscribers = {}
        self.subscriber_data = {}
        self.subscribers['Camera'] = self.create_subscription(Image,'/camera/image_raw',lambda msg: self._UpdateData(msg,'Camera'),10)
        self.subscribers['Lidar'] = self.create_subscription(LaserScan,'/scan',lambda msg: self._UpdateData(msg,'Lidar'),10)
        self.subscribers['SysHP'] = self.create_subscription(DiagnosticArray,'/system_health',lambda msg: self._UpdateData(msg,'SysHP'),10)


        self.subscriber_data["Lidar"] = []
        self.subscriber_data['SysHP'] = {}

    def Spin(self):
        # Spin self (as self is a node)
        try:
            # Keep the node running and processing callbacks
            rclpy.spin(self)
        except KeyboardInterrupt:
            # Allow graceful shutdown with Ctrl+C
            pass
        finally:
            # Clean up
            self.destroy_node()
            rclpy.shutdown()


    def _UpdateData(self,msg,id):

        if (id in self.subscribers.keys()):
            self.subscriber_data[id] = self.decoder.Decode_Msg(msg,id)

            if (id == 'Lidar'):
                self.subscriber_data['unique'] = msg


    async def GetData(self,id:String, gui_pipe: Pipe):

        if id in self.subscribers.keys():
            while True:
                await asyncio.sleep(1)
                gui_pipe.send(np.array(self.subscriber_data[id]))
        else:
            # Throw warning
            pass

    def Publish(self,id,msg):
        pass

class Decoder():

    def Decode_Msg(self,msg,id):

        match id:

            case 'Lidar':
                return self._Decode_Scan(msg)
            
            case 'SysHP':
                return self._Decode_DiagnosticArray(msg)
            
            case _:
                return msg

    
    def _Decode_Scan(self,msg):
        header = msg.header
        range = msg.ranges
        angle_min = msg.angle_min
        angle_max = msg.angle_max
        angle_increment  = msg.angle_increment
        range_min = msg.range_min
        range_max = msg.range_max

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

    def _Decode_DiagnosticArray(self,msg):

        return_dict = {}

        for sub_msg in msg.status:
            return_dict[sub_msg.name] = sub_msg.message
        
        return return_dict

