################################
# node_handler.py
# Part of the user_interface_py_pkg
#
# Author: Nathan Horder (nathan.horder.700@cranfield.ac.uk)
# Part of Cranfield University MSC Robotics Group Project 2025-2026
################################

import rclpy
from rclpy.node import Node
import asyncio
import json
import numpy as np
import cv2 as cv
from holoviews.streams import Pipe
from std_msgs.msg import String
from diagnostic_msgs.msg import DiagnosticArray
from sensor_msgs.msg import LaserScan, Image
from cv_bridge import CvBridge

"""
NodeHandler
Class to handle connection between the user interface and ROS2 nodes
"""
class NodeHandler(Node):
    
    def __init__(self,dev_mode=False):

        super().__init__('gui_node_handler')
        self.decoder = Decoder()
        self.dev_mode = dev_mode

        self.subscribers = {}
        self.subscriber_data = {}
        self.subscribers['Camera'] = self.create_subscription(Image,'/camera/image_raw',lambda msg: self._UpdateData(msg,'Camera'),10)
        self.subscribers['Lidar'] = self.create_subscription(LaserScan,'/processed/scan',lambda msg: self._UpdateData(msg,'Lidar'),10)
        self.subscribers['SysHP'] = self.create_subscription(DiagnosticArray,'/system_health',lambda msg: self._UpdateData(msg,'SysHP'),10)
        self.subscribers['Wall_Visual'] = self.create_subscription(String,'/wall/designation',lambda msg: self._UpdateData(msg,'Wall_Visual'),10)

        self.subscriber_data["Lidar"] = []
        self.subscriber_data['Camera'] = []
        self.subscriber_data['SysHP'] = {}
        self.subscriber_data['Wall_Visual'] = []

        self.nodes = {}
        self.nodes["Current_Action"] = self.create_publisher(String,'/gui/action',10)


    def Spin(self):
        """
        Spin (Public)
        Method to spin self, enabling running of subscriber and publisher nodes
        Executed on a separate thread - will block main thread if called from main thread

        Arguments: N/A

        Returns: N/A
        """
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


    def _UpdateData(self,msg,id:str):
        """
        _UpdateData (Private)
        Callback method for subscribers, updates local data store

        Arguments
            - <variable_type>: msg || ROS2 inbound message
            - str : id || Which type of messsage is being sent (I/e Lidar, Camera, SysHP, Wall_Visual, etc)

        Returns: N/A
        """
        if (id in self.subscribers.keys()):
            self.subscriber_data[id] = self.decoder.DecodeMsg(msg,id)

            if (id == 'Lidar'):
                self.subscriber_data['unique'] = msg


    async def GetDataAsync(self,id:String, gui_pipe: Pipe):
        """
        GetDataAsync (Public)
        Aync method for retrieving data from subscriber
        Used for HoloViews graphics, alternative is GetData

        Arguments
            - str : id || The subscriber to retrieve data from
            - Pipe : gui_pipe || Related GUI pipe to send the data through

        Returns: N/A
        """
        if id in self.subscribers.keys():
            while True:
                await asyncio.sleep(1)
                gui_pipe.send(np.array(self.subscriber_data[id]))
        else:
            # Throw warning
            pass
    

    def GetData(self,id:String):
        """
        GetData (Public)
        Method for retrieving data from a subscriber
        Method for general data access, alternative is GetDataAsync for HoloViews specific graphics

        Arguments
            - str : id || Subscriber to access data from

        Returns:
            - <variable_type>  || Subscriber data
        """
        if id in self.subscribers.keys():
            return self.subscriber_data[id]
    

    def Publish(self,id,data):
        """
        Publish (Public)
        Method to publish results to a specific subscriber

        Arguments
            - str : id || The publisher to publish the message
            - <variable_type>: data || The message to be published

        Returns: N/A
        """

        if id == "Current_Action":
            msg = String()
            
            if data == None or data.wall == None:
                msg.data = "None"
            else:
                msg.data = data.wall

            self.nodes["Current_Action"].publish(msg)
        
        
"""
Decoder
Class to decode ROS2 messages into usable formats

Main function: Decode_Msg
    - Argument: <variable_type> : msg || ROS2 inbound message
    - Argument: str : id || Which type of messsage is being sent (I/e Lidar, Camera, SysHP, Wall_Visual, etc)
    - Return: <variable_type> || Decoded message
"""
class Decoder():

    def DecodeMsg(self,msg,id:str):
        """
        DecodeMsg (Public)
        Main method for Decoder class, handles processing / direction of processing provided message

        Arguments
            - <variable_type>: msg || ROS2 inbound message
            - str : id || Which type of messsage is being sent (I/e Lidar, Camera, SysHP, Wall_Visual, etc)

        Returns:
            - <variable_type>  || Decoded message
        """

        match id:

            case 'Lidar':
                return self._DecodeScan(msg)
            
            case 'Camera':
                return self._DecodeImage(msg)
            
            case 'SysHP':
                return self._DecodeDiagnosticArray(msg)
            
            case 'Wall_Visual':
                return self._DecodeJSON(msg,True)
            
            case _:
                return msg

    def _DecodeScan(self,msg:LaserScan):
        """
        _DecodeScane (Private)
        Method to decode LaserScan ROS2 message

        Arguments
            - LaserScan: msg || ROS2 inbound message

        Returns:
            - list : points || List of (x,y) coordinates for each range

        """
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

    def _DecodeDiagnosticArray(self,msg:DiagnosticArray):
        """
        _DecodeDiagnosticArray (Private)
        Method to decode DiagnosticArray ROS2 messages

        Arguments
            - DiagnosticArray: msg || Inbound ROS2 message

        Returns:
            - dict : return_dict || Dictionary containing array information

        """

        return_dict = {}

        for sub_msg in msg.status:
            return_dict[sub_msg.name] = sub_msg.message
        
        return return_dict

    def _DecodeJSON(self,msg:String,IsWallVisual=False):
        """
        _DecodeJSON (Private)
        Method to decode String (/ JSON) ROS2 messages

        Arguments
            - String : msg || Inbound ROS2 message
            - bool : IsWallVisual || Factor to change decoding based on publisher - Default is False

        Returns:
            - dict || Decoded message, often presented as a dictionary - may be a list instead 
            - (isWallVisual = True) np.array || Array of wall data
        """

        if not IsWallVisual: return json.loads(msg.data)
        else:

            data = json.loads(msg.data)
            # data = [ [x0,y0,x1,y2,'name',dir] ]

            joined_lines = []
            links = {}
            txt = "Wall "
            count = 1

            for loop in range(1,len(data)-1):
                if data[loop][5] == data[loop+1][5]:
                    joined_lines.append([data[loop][0],data[loop][1],data[loop+1][2],data[loop+1][3],txt+str(count)])
                    links[data[loop+1][4]] = [data[loop],data[loop+1],txt+str(count)]
                    count+=1
                elif not data[loop][4] in links.keys():
                    joined_lines.append([data[loop][0],data[loop][1],data[loop][2],data[loop][3],txt+str(count)])
                    count+=1
                
            return np.array(joined_lines)

    def _DecodeImage(self,msg:Image):
        """
        _DecodeImage (Private)
        Method to decode Image ROS2 messages

        Arguments
            - Image : msg || Inbound ROS2 message

        Returns:
            - ndarray img : frame || Image in format useable by OpenCV

        """
        frame = CvBridge().imgmsg_to_cv2(msg)
        return frame

