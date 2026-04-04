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

    # TODO: Student should create a sublaunch for the turtlebot main behavior and include it here. 
    #       The sublaunch should be named remote_chassis.launch.py and should contain the movement node.
    #        
    #       Currently, the remte_chassis.launch.py file contains the teleop_twist_keyboard node, 
    #       but it is not usable. Replace the teleop_twist_keyboard node with the movement node 
    #       that you created in the previous step.

    # chassis_launch = PathJoinSubstitution([
    #     ThisLaunchFileDir(),
    #     'remote_chassis.launch.py',
    # ])

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(rplidar_launch)
        ),
        
        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource(chassis_launch)
        # ),
    ])