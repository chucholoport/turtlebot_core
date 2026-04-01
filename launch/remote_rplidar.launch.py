from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch.substitutions import ThisLaunchFileDir
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():

    rviz_config = PathJoinSubstitution([
        ThisLaunchFileDir(),
        '..',
        'rviz',
        'view_rplidar.rviz'
    ])

    return LaunchDescription([

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config],
        )

    ])