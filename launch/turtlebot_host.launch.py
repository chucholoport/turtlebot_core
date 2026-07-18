from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution
from launch.substitutions import ThisLaunchFileDir
from launch_ros.actions import Node


def generate_launch_description():

    # Config de RViz2 con lidar + camara + TF
    rviz_config = PathJoinSubstitution([
        ThisLaunchFileDir(),
        '..',
        'rviz',
        'view_camera.rviz',
    ])

    # chassis_launch = PathJoinSubstitution([
    #     ThisLaunchFileDir(),
    #     'chassis.launch.py',
    # ])

    return LaunchDescription([

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config],
        ),

        # El chassis queda desactivado en el host: su backend (uno_q_bridge o
        # micro-ROS para ESP32) depende de la plataforma que lo despliegue, por
        # eso se lanza desde el edge (turtlebot_edge.launch.py). Para activarlo
        # aqui, descomenta el include y ajusta el chassis_backend:
        #
        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource(chassis_launch),
        #     launch_arguments={'chassis_backend': 'uno_q'}.items(),
        # ),
    ])
