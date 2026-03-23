#!/usr/bin/python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import CompressedImage, Image
from std_msgs.msg import Empty
from cv_bridge import CvBridge
import cv2
import numpy as np
from include.qr import quick_detect_qr


from picamera2 import Picamera2
from libcamera import Transform



class PicamPublisher(Node):
    def __init__(self):
        super().__init__('picam_driver')

        # Initialise the camera
        self.camera = None
        self.setup_camera()
        

        # Store current camera mode: still or stream
        self.isStill = False


        # Create a QoS Profile to prevent re-sending failed image messages, that can cause network issues with such data
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )


        # Declare parameters
        self.declare_parameter('enable_qr', False)
        self.qrEnabled = self.get_parameter('enable_qr').get_parameter_value().bool_value

        
        # Create a publisher for the low res camera feed
        self.stream_publisher = self.create_publisher(CompressedImage, 'camera/detection_feed/compressed', qos_profile)
        
        self.vslam_stream_publisher = self.create_publisher(Image, 'camera/image_raw', 1)

        # Create a publisher for the high res still image
        self.still_publisher = self.create_publisher(CompressedImage,'camera/still_image/compressed', 10)

        
        # Create a CvBridge instance
        self.bridge = CvBridge()
        
        # Start a timer to publish frames at 20hZ
        self.timer = self.create_timer(0.05, self.publish_frame)

        
        # Subscribe to take_picture
        self.create_subscription(Empty,'take_picture', self.still_request, 10) # What datatype will take_picture publish? Assumed string




    def setup_camera(self):
        """Initialise camera settings and start stream"""
        # Create camera
        self.camera = Picamera2()


        # Get sensor modes
        modes = self.camera.sensor_modes

        # Log
        print("Available sensor modes:")
        for e in modes:
            print(f"- {e}")
        print(f"Full resolution for still image: {self.camera.sensor_resolution}")

        # Flip images
        transform = Transform(hflip=True, vflip=True)


        # Define resolutions
        full_res = self.camera.sensor_resolution
        low_res = (720, 405)
        low_res_sensor_mode = modes[1]

        # Create streaming config
        self.stream_config = self.camera.create_video_configuration(
            # Select lowest resolution that has full size no crop
            sensor={
                'output_size': low_res_sensor_mode['size'],
                'bit_depth': low_res_sensor_mode['bit_depth']
            },
            # Reduce stream resolution
            main={'size': low_res, 'format': 'RGB888'},
            # Set framerate to 20fps
            controls={"FrameDurationLimits": (50000, 50000)},
            transform= transform
        )

        # Create still image config
        self.still_config = self.camera.create_still_configuration(
            main={'size': full_res, 'format': 'RGB888'},
            transform=transform
        )
        
        # Initialise stream
        self.camera.configure(self.stream_config)

        self.camera.start()


    def publish_frame(self):
        # Get image from camera as numpy array
        image = self.camera.capture_array("main")

        # Publish raw image for vslam
        msg = self.bridge.cv2_to_imgmsg(image,"bgr8")
        self.vslam_stream_publisher.publish(msg)


        # Publish image for feed for teleop
        if self.qrEnabled:
            # Detect QR codes in the frame
            image = quick_detect_qr(image)

        # Convert the image to grayscale for less data
        gray_img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Convert the frame to a ROS Image message
        msg = self.bridge.cv2_to_compressed_imgmsg(gray_img)
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera_link"
        
        # Publish the message
        self.stream_publisher.publish(msg)



    # When signal received from take_picture, publish high resolution still image
    def still_request(self, _):
        self.get_logger().info(f'Received request on take_picture. Publishing still image...')

        # Change from low res to high res and take one image
        image = self.camera.switch_mode_and_capture_array(self.still_config, "main")
        
        # Convert the latest frame to a ROS Image message
        still_image_msg = self.bridge.cv2_to_compressed_imgmsg(image)
        still_image_msg.header.stamp = self.get_clock().now().to_msg()
        still_image_msg.header.frame_id = "camera_link"
        
        # Publish to detection
        self.still_publisher.publish(still_image_msg)


    def __del__(self):
        if self.camera is not None:
            self.camera.stop()



def main(args=None):
    rclpy.init(args=args)
    node = PicamPublisher()
    
    rclpy.spin(node)
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
