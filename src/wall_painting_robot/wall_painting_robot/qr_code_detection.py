import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge
import cv2
import zxingcpp
import numpy as np

class PublisherSubscriberNode(Node):
    def __init__(self):
        super().__init__('qr_code_detection')

        #C onverts ROS image to OpenCV image
        self.bridge = CvBridge() 

        # Latest frame storage
        self.latest_frame = None


        # Create a QoS Profile to prevent re-sending failed image messages, that can cause network issues with such data
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )


        # Publish live feed to 'detection_feed'
        self.detectionFeedPublisher = self.create_publisher(CompressedImage, 'camera/detection_feed/compressed', qos_profile)




        # Subscribe to camera/image_raw"
        self.create_subscription(CompressedImage,'camera/image_raw/compressed', self.camera_callback, qos_profile)
       



    def detect_qr(self):
        if self.latest_frame is None:
            self.get_logger().warning("No frame available for QR detection")
            return
        
        # Convert ROS Image message to OpenCV format
        frame = self.latest_frame.copy()

        # Detect QR codes in the frame
        decoded_objects = zxingcpp.read_barcodes(frame)

        for obj in decoded_objects:
            # Default color is red for detected QR codes
            color = (0, 0, 255)            

            # If data can be read, set the color to green
            if obj.text and obj.format == zxingcpp.BarcodeFormat.QRCode:
                self.get_logger().info(f"QR Code detected: {obj.text}")
                color = (0, 255, 0)
                
            # Draw polygon around the QR code
            pts = np.intp([(obj.position.top_left.x, obj.position.top_left.y), (obj.position.top_right.x, obj.position.top_right.y), (obj.position.bottom_right.x, obj.position.bottom_right.y), (obj.position.bottom_left.x, obj.position.bottom_left.y)])
            cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=2)
  

        # Resize image
        newImage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        newImage = cv2.resize(newImage, (800,600))


        # Convert the modified frame back to ROS Image message
        processed_msg = self.bridge.cv2_to_compressed_imgmsg(newImage)
        processed_msg.header.stamp = self.get_clock().now().to_msg()
        processed_msg.header.frame_id = "camera"

        self.detectionFeedPublisher.publish(processed_msg)






    # When signal received from camera, convert image to OpenCV type, check for qr code
    def camera_callback(self, msg:CompressedImage):
        self.latest_frame = self.bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8')
        self.detect_qr()




def main(args=None):
    rclpy.init(args=args)
    node = PublisherSubscriberNode()

    rclpy.spin(node)  # Keep the node running

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()