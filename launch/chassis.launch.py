from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            name='uno_q_bridge',
            package='uno_q_bridge',
            executable='chassis_bridge',
            output='screen',
        ),
    ])
