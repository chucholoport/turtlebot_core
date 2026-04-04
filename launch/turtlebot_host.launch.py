from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution
from launch.substitutions import ThisLaunchFileDir

def generate_launch_description():

    rplidar_launch = PathJoinSubstitution([
        ThisLaunchFileDir(),
        'remote_rplidar.launch.py',
    ])

    chassis_launch = PathJoinSubstitution([
        ThisLaunchFileDir(),
        'remote_chassis.launch.py',
    ])

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(rplidar_launch)
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(chassis_launch)
        ),
    ])