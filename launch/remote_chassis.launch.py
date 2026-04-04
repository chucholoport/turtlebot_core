from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='teleop_twist_keyboard',
            executable='teleop_twist_keyboard',  # teleop_joystick
            name='teleop_twist_keyboard',
            output='screen',
            prefix='xterm -e'
        ),
    ])