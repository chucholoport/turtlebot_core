#!/usr/bin/env python3

"""
ROS 2 node that periodically toggles an internal LED state and publishes
the result to a topic.

The node uses a timer to invert the LED state at a fixed interval and
publishes the updated value to the '/set_led' topic as a Bool message.
This node does not interact directly with hardware; it is intended to
drive a separate bridge node responsible for hardware communication.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool


class ToggleLedNode(Node):
    """Node that periodically toggles and publishes an LED state."""

    def __init__(self):
        """Initialize the node, internal state, publisher, and timer."""
        super().__init__('toggle_led_node')

        # Internal LED state (False = OFF, True = ON)
        self.led_state = False

        # Publisher for setting LED state
        self._pub = self.create_publisher(
            Bool,
            'set_led',
            10
        )

        # Timer to toggle LED state every second
        self._timer = self.create_timer(
            1.0, 
            self.toggle_led
        )

        self.get_logger().info("Toggle LED node started.")

    def toggle_led(self) -> None:
        """Toggle the internal LED state and publish the new value.

        This method updates the internal state and sends the result
        to the '/set_led' topic.
        """
        # Toggle internal state
        self.led_state = not self.led_state

        # Create and publish message
        msg = Bool()
        msg.data = self.led_state
        self._pub.publish(msg)

        self.get_logger().debug(
            f"Published LED state: {self.led_state}"
        )


def main(args=None):
    """Initialize ROS 2, create the node, and start spinning."""
    rclpy.init(args=args)

    node = ToggleLedNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()