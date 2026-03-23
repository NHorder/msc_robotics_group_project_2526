import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from tf2_ros import TransformListener, Buffer, TransformException
from cv_bridge import CvBridge
import cv2
import zxingcpp
from pyzbar.pyzbar import decode, ZBarSymbol
import numpy as np
import math
import os
import re
import glob
import subprocess


class SimpleResult:
    def __init__(self, t, points):
        self.text = t
        self.points = points

class FeatureDetectionNode(Node):
    def __init__(self):
        # initialise node
        super().__init__('feature_processing')


        #subscribe to tf
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        # self.timer = self.create_timer(0.5, self.lookup_tf)

        #store separate rocks
        self.rocks = []
        self.rock_counter = 1

        self.img_id = 1

        self.smallest_images = ["","","","","",""]

        # subscribe to the still image
        self.create_subscription(CompressedImage,'camera/still_image/compressed', self.feature_callback, 10) 

        self.declare_parameter("folder_path", "/home/ORT_QR")
        self.path = self.get_parameter("folder_path").get_parameter_value().string_value

        if not os.path.exists(self.path):
            os.makedirs(self.path)
            self.get_logger().info(f"Created folder at {self.path}")

    
    # when an image is received
    def feature_callback(self,msg):
        #default in case cannot extract/assign rock
        qr_data = "No QR code detected"
        rock_label = "unknown rock"

        # Convert ROS Image message to OpenCV format
        frame = CvBridge().compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8')
        
        # Save with unique ID
        filename = os.path.join(self.path, f"rock_image_{self.img_id:03d}.jpeg")
        cv2.imwrite(filename, frame)
        self.get_logger().info(f"Saved image #{self.img_id} to {filename}")
        

        # Lookup tf to get coordinates
        qrcode_location = self.lookup_tf()
        

        # Detect QR codes in the frame
        decoded_objects = self.barcode_reader(frame)
        # If cannot read QR code, try image processing
        if not decoded_objects:
            decoded_objects = self.image_processing(frame)



        #Assign rock number
        rock_label = self.rock_assignment(qrcode_location)

        #Publish to .txt file
        self.log_detection(self.img_id, qrcode_location, rock_label, qr_data)

        qr_code = 1


        # Draw square around QR codes
        for obj in decoded_objects:
            points = obj.points if hasattr(obj, 'points') else None
            if points is not None:
                self.drawSquare(frame, points)
       

        # Extract data
        for obj in decoded_objects:
            qr_data = obj.text  #Assume data stored as string
            self.get_logger().info(f"Decoded QR Code data: {qr_data}")

            # If data extracted, save to individual rock folder
            if qr_data != "No QR code detected" and not qr_data.strip().isdigit():
                if qr_code == 1:
                    rock_folder = os.path.join(self.path, rock_label)
                    os.makedirs(rock_folder, exist_ok=True)

                    email_folder = os.path.join(self.path, "to_email", rock_label)
                    os.makedirs(email_folder, exist_ok=True)

                    rock_path = os.path.join(rock_folder, f"rock_image_{self.img_id:03d}.jpeg")
                    cv2.imwrite(rock_path, frame)
                    os.remove(os.path.join(self.path, f"rock_image_{self.img_id:03d}.jpeg"))
                    
                    self.get_logger().info(f"✅ Saved image #{self.img_id} to {rock_path}")
                    log_path = os.path.join(rock_folder,f"{rock_label}_summary.txt")
                    logged_data = set()

                #Publish to .txt file
                self.log_detection(self.img_id - 1, qrcode_location, rock_label, qr_data)

                #Add extracted data to summary file in rock folder
                if os.path.exists(log_path):
                    with open(log_path, "r") as log_file:
                        for line in log_file:
                            logged_data.add(line.strip().lower())
                            

                if qr_data.strip().lower() not in logged_data and not qr_data.strip().isdigit():
                    with open(log_path, "a") as log_file:
                        log_file.write(f"{qr_data.strip()}\n")
                    self.get_logger().info(f"✅ Added {qr_data} to {rock_label} summary file")

                #If smallest image, save to folder for email
                
                files = glob.glob(f"{email_folder}/*")
                email_path = f"{email_folder}/rock_image_{self.img_id:03d}.jpeg"
                size_priority = {"S": 0, "M": 1, "L": 2}

                index = int(rock_label.split("_")[1]) - 1

                current_size = self.smallest_images[index]

                if qr_data.startswith("S -"):
                    new_size = "S"
                elif qr_data.startswith("M -"):
                    new_size = "M"
                else:
                    new_size = "L"

                should_replace = (current_size == "" or size_priority[new_size] < size_priority[current_size])

                if should_replace:
                    for f in files:
                        os.remove(f)

                    save_path = os.path.join(email_folder, f"rock_image_{self.img_id:03d}.jpeg")
                    cv2.imwrite(save_path, frame)

                    self.smallest_images[index] = new_size
                    self.get_logger().info(f"✅ {new_size} image saved to email folder")
            qr_code+=1

        
        self.img_id += 1




    def lookup_tf(self):
        try:
            now = rclpy.time.Time()
            trans = self.tf_buffer.lookup_transform(
                target_frame='odom',  # <- change to your global/world frame
                source_frame='rock_link',  # <- change to your robot/camera frame
                time=now
                )
            x = trans.transform.translation.x
            y = trans.transform.translation.y
            self.get_logger().info(f"📍 Image taken at position: ({x:.2f}, {y:.2f})")
            return (x, y)

        except TransformException as e:
            self.get_logger().warn(f"TF lookup failed: {str(e)}, using default coordinates (0, 0)")
            return (0.0, 0.0)

    def image_processing(self, image):
        mtx = np.array([[1.99225240e+03,0.00000000e+00,2.30787097e+03],
                [0.00000000e+00,1.99069688e+03,1.29404010e+03],
                [0.00000000e+00,0.00000000e+00,1.00000000e+00]])

        dist = np.array([[-0.05049456,0.0724151,0.00104795,0.00132452,-0.03986304]])

        h, w = image.shape[:2]

        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        self.get_logger().info("Image processing may take a minute")
        processing_pipeline = [
            lambda img: img,  # Original
            lambda img: cv2.undistort(img, mtx, dist, None, newcameramtx),
            lambda img: cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
            lambda img: cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)),
            lambda img: cv2.adaptiveThreshold(
                cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2,
            ),
            lambda img: cv2.resize(img, None, fx=2.0, fy=2.0),
            ]

        for i, step in enumerate(processing_pipeline):
            processed = step(image)
            results = self.barcode_reader(processed)
            if results:
                return results  # returns a list of result objects

        self.get_logger().info("⚠️ QR code could not be extracted with any method")
        return []



    def barcode_reader(self, image):
        decoded_objects = zxingcpp.read_barcodes(image)

        if decoded_objects:
            return [SimpleResult(obj.text, [np.intp([(obj.position.top_left.x, obj.position.top_left.y), (obj.position.top_right.x, obj.position.top_right.y), (obj.position.bottom_right.x, obj.position.bottom_right.y), (obj.position.bottom_left.x, obj.position.bottom_left.y)])]) for obj in decoded_objects]

        opencvDetector = cv2.QRCodeDetector()
        text, points, _ = opencvDetector.detectAndDecode(image)
        if text:
            return [SimpleResult(text, points)]

        decoded_objects = decode(image, symbols=[ZBarSymbol.QRCODE])
        if decoded_objects:
            return [SimpleResult(obj.data, [np.array([(point.x, point.y) for point in obj.polygon], dtype=np.int32).reshape((-1, 1, 2))]) for obj in decoded_objects]

        return []

    def drawSquare(self, img, points):
        cv2.polylines(img, points, isClosed=True, color=(0, 255, 0), thickness=5)

    def rock_assignment(self, location):
         x_new, y_new = location
         for rock in self.rocks:
             x_old, y_old = rock["position"]
             dist = math.sqrt((x_new - x_old)**2 + (y_new - y_old)**2)
             
             #if less than 2 meters to a previous rock, assign same rock
             if dist < 2.0:
                 #Rock coordinates average of all points
                 x_av = (x_old+x_new)/2
                 y_av = (y_old+y_new)/2
                 rock["position"] = x_av, y_av
                 return rock["label"]
        # If no close match, make a new rock
         new_label = f"rock_{self.rock_counter}"
         self.rocks.append({
             "position": location,
             "label": new_label
             })
         self.rock_counter += 1
         return new_label
        
    def log_detection(self, image_id, image_location, rock_label, qr_data):
        for rock in self.rocks:
             if rock["label"] == rock_label:
                    x, y = rock["position"]
                    dist = math.sqrt(x**2 + y**2)
        log_path = os.path.join(self.path, "rock_detections.txt")
        with open(log_path, "a") as log_file:
            log_file.write(f"Image {image_id:03d}, Image location: {image_location}, Rock: {rock_label}, QR Data: {qr_data}, Estimated rock position: {rock['position']}, Estimated distance from start: {dist}\n")

    def write_final_positions(self):
        log_path = os.path.join(self.path, "rock_detections.txt")
        with open(log_path, "r") as log_file:
            lines = log_file.readlines()
        new_lines = []
        for line in lines:
            if not line.strip():
                new_lines.append(line)
                continue

            match = re.search(r"Rock:\s*([^\s,]+)", line)
            if match:
                rock_label = match.group(1).strip()
            else:
                new_lines.append(line)
                continue

            updated = False
            for rock in self.rocks:

                if rock["label"] == rock_label:
                    x, y = rock["position"]
                    dist = math.sqrt(x**2 + y**2)
                
                    line = (
                        line.strip() + f", Rock location: {rock['position']}, Distance from start: {dist}\n")
                    updated = True
                    break
            new_lines.append(line)
        with open(log_path, "w") as f:
            f.writelines(new_lines)
        self.get_logger().info(f"✅ Final positions saved to {log_path}")



def main(args=None):
    rclpy.init(args=args)
    node = FeatureDetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Node interrupted by user.")
    finally:
        node.write_final_positions()
        subprocess.run(["/usr/bin/python3", "ROS2_ws/src/wall_painting_robot/wall_painting_robot/emailer.py"]) # TODO: fix this path
        node.destroy_node()

if __name__ == '__main__':
    main()
