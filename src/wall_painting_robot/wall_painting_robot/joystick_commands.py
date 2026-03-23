import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import Empty

class JoystickCommands(Node):
    def __init__(self):
        super().__init__('joystick_commands')
        
        # Subscribe to joy messages 
        self.create_subscription(Joy, 'joy', self.receiveJoystickCommand, 10)

        # Create a publisher to request the camera still image
        self.still_publisher = self.create_publisher(Empty, 'take_picture', 10)

        # Create a publisher to request led toggle
        self.led_publisher = self.create_publisher(Empty, 'led', 10)


        # Declare parameters for joystick buttons
        self.declare_parameters('',[
            ('still_button', 0),  # Default button for taking a picture
            ('led_button', 1)     # Default button for toggling the LED
        ])

        self.stillBtnID = self.get_parameter('still_button').get_parameter_value().integer_value
        self.ledBtnID   = self.get_parameter('led_button').get_parameter_value().integer_value

        # Initialize previous button states to avoid repeated commands
        self.previousStillBtnValue = 0
        self.previousLedBtnValue = 0
        

    def receiveJoystickCommand(self, msg:Joy):
        # If corresponding button pressed, ask camera to send picture
        if msg.buttons[self.stillBtnID] == 1 and self.previousStillBtnValue == 0:
            self.still_publisher.publish(Empty())


        # If corresponding button pressed, toggle led
        if msg.buttons[self.ledBtnID] == 1 and self.previousLedBtnValue == 0:
            self.led_publisher.publish(Empty())


        # Save previous button states to avoid repeated commands
        self.previousStillBtnValue = msg.buttons[self.stillBtnID]
        self.previousLedBtnValue   = msg.buttons[self.ledBtnID]



def main(args=None):
    rclpy.init(args=args)
    node = JoystickCommands()
    
    rclpy.spin(node)
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
