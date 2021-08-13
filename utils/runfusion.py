from b360.msg import DetectionStructure,RadarMessage,RadarStatusMessage
import rclpy
from rclpy.node import Node
import time

class Fusion(Node):

    def __init__(self):
        super().__init__('fusion')
        self.subscription = self.create_subscription(
            RadarMessage,
            '/Radar_1',
            self.listener_callback)
        self.subscription  # prevent unused variable warning
        self.subscription = self.create_subscription(
            RadarMessage,
            '/Radar_2',
            self.listener_callback)
        self.subscription  # prevent unused variable warning
        self.subscription = self.create_subscription(
            RadarMessage,
            '/Radar_3',
            self.listener_callback)
        self.subscription = self.create_subscription(
            RadarMessage,
            '/Radar_4',
            self.listener_callback)
        self.subscription  # prevent unused variable warning
        self.subscription = self.create_subscription(
            RadarMessage,
            '/Radar_5',
            self.listener_callback)
        self.subscription  # prevent unused variable warning
        self.subscription = self.create_subscription(
            RadarMessage,
            '/Radar_6',
            self.listener_callback)
        self.subscription  # prevent unused variable warning
        self.subscription = self.create_subscription(
            RadarMessage,
            '/Radar_7',
            self.listener_callback)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.ip)



def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = Fusion()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
