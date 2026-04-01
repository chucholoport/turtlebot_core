#!/usr/bin/env python3

"""
ROS 2 node that allows manual control of an LED state via console input.

The node reads user input from the terminal and publishes Boolean messages
to the '/set_led' topic. The user can turn the LED on or off interactively.
Execution stops when the user presses 'q'.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool


class ControlLedNode(Node):
    """Node that publishes LED commands based on user input."""

    def __init__(self):
        """Initialize the node and publisher."""
        super().__init__('control_led_node')

        self._pub = self.create_publisher(
            Bool,
            'set_led',
            10
        )

        self.get_logger().info("Control LED node started.")

    def run(self) -> None:
        """Run the input loop and publish LED commands."""
        self.get_logger().info(
            "Enter '1' to turn ON, '0' to turn OFF, 'q' to quit."
        )

        while rclpy.ok():
            try:
                user_input = input(">> ").strip()

                if user_input == 'q':
                    self.get_logger().info("Shutting down control node.")
                    break

                elif user_input in ('0', '1'):
                    msg = Bool()
                    msg.data = (user_input == '1')
                    self._pub.publish(msg)

                    self.get_logger().debug(
                        f"Published LED state: {msg.data}"
                    )

                else:
                    self.get_logger().warning(
                        "Invalid input. Use '1', '0', or 'q'."
                    )

            except (EOFError, KeyboardInterrupt):
                self.get_logger().info("Interrupted by user.")
                break


def main(args=None):
    """Initialize ROS 2, create the node, and process user input."""
    rclpy.init(args=args)

    node = ControlLedNode()

    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()