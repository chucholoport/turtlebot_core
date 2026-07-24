from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    # Parametrizado para que edge.launch.py inyecte los valores de
    # robot.ini. Tambien funciona por si solo con los defaults de abajo.
    serial_port = LaunchConfiguration('serial_port')
    serial_baudrate = LaunchConfiguration('serial_baudrate')
    frame_id = LaunchConfiguration('frame_id')

    return LaunchDescription([
        DeclareLaunchArgument(
            'serial_port',
            default_value='/dev/rplidar',
            description='Puerto serie del RPLidar',
        ),
        DeclareLaunchArgument(
            'serial_baudrate',
            default_value='115200',
            description='Baudrate del RPLidar: A1/A2 = 115200, A3 = 256000',
        ),
        DeclareLaunchArgument(
            'frame_id',
            default_value='laser',
            description='Frame TF del rplidar',
        ),

        Node(
            name='rplidar_composition',
            package='rplidar_ros',
            executable='rplidar_composition',
            output='screen',
            parameters=[{
                'serial_port': serial_port,
                'serial_baudrate': ParameterValue(serial_baudrate, value_type=int),
                'frame_id': frame_id,
                'inverted': False,
                'angle_compensate': True,
            }],
        ),
    ])
