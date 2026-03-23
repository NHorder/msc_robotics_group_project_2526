import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import Empty
from cv_bridge import CvBridge
import cv2
from include.qr import quick_detect_qr

class WebcamPublisher(Node):
    def __init__(self):
        super().__init__('webcam_publisher')
        
        # Initialize the OpenCV capture
        self.cap = cv2.VideoCapture(0)  # Use 0 for the default webcam
        
        if not self.cap.isOpened():
            self.get_logger().error("Failed to open webcam")
            return
        

        # Create a QoS Profile to prevent re-sending failed image messages, that can cause network issues with such data
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.lastFrame = None


        # Declare parameters
        self.declare_parameter('enable_qr', False)
        self.qrEnabled = self.get_parameter('enable_qr').get_parameter_value().bool_value

        
        # Create a publisher for the camera feed
        self.stream_publisher = self.create_publisher(CompressedImage, 'camera/detection_feed/compressed', qos_profile)


        # Create a publisher for the high res still image
        self.still_publisher = self.create_publisher(CompressedImage,'camera/still_image/compressed', 10)

        # Subscribe to take_picture
        self.create_subscription(Empty, 'take_picture', self.still_request, 10) # What datatype will take_picture publish? Assumed string
        
        # Create a CvBridge instance
        self.bridge = CvBridge()
        
        # Start a timer to publish frames every 0.1 seconds
        self.timer = self.create_timer(0.1, self.publish_frame)



    def publish_frame(self):
        # Capture a frame from the webcam
        ret, self.lastFrame = self.cap.read()
        if not ret:
            self.get_logger().warning('Failed to capture image')
            return
        

        if self.qrEnabled:
            # Detect QR codes in the frame
            frame = quick_detect_qr(self.lastFrame.copy())
        else:
            # If QR detection is not enabled, just use the original frame
            frame = self.lastFrame
    

        # Convert the image to grayscale for less data
        gray_img = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)


        # Convert the frame to a ROS Image message
        msg = self.bridge.cv2_to_compressed_imgmsg(gray_img)
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera"
            
            
        # Publish the message
        self.stream_publisher.publish(msg)


    
    # When signal received from take_picture, publish high resolution still image
    def still_request(self, _):
        self.get_logger().info(f'Received request on take_picture. Publishing still image...')
        
        # Convert the latest frame to a ROS Image message
        still_image_msg = self.bridge.cv2_to_compressed_imgmsg(self.lastFrame)
        
        # Publish the message
        still_image_msg.header.stamp = self.get_clock().now().to_msg()
        still_image_msg.header.frame_id = "camera"
        self.still_publisher.publish(still_image_msg)


    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()




def main(args=None):
    rclpy.init(args=args)
    node = WebcamPublisher()
    
    rclpy.spin(node)
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
