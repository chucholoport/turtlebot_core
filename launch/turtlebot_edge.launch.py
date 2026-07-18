from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch.substitutions import ThisLaunchFileDir


def generate_launch_description():

    # ------------------------------------------------------------------
    # Argumentos del chassis (se reenvian a chassis.launch.py). Permiten
    # elegir el backend desde el propio edge segun la plataforma, p.ej:
    #   ros2 launch turtlebot_core turtlebot_edge.launch.py chassis_backend:=microros microros_transport:=serial
    # ------------------------------------------------------------------
    chassis_backend = LaunchConfiguration('chassis_backend')
    microros_transport = LaunchConfiguration('microros_transport')
    serial_device = LaunchConfiguration('serial_device')
    serial_baudrate = LaunchConfiguration('serial_baudrate')
    udp_port = LaunchConfiguration('udp_port')

    declare_chassis_backend = DeclareLaunchArgument(
        'chassis_backend',
        default_value='uno_q',
        choices=['uno_q', 'microros'],
        description='Backend del chassis: "uno_q" (uno_q_bridge) o "microros" '
                    '(micro-ROS agent para ESP32 con ESP-IDF 5.4)',
    )
    declare_microros_transport = DeclareLaunchArgument(
        'microros_transport',
        default_value='serial',
        choices=['serial', 'udp4'],
        description='Transporte del micro-ROS agent (solo aplica si chassis_backend:=microros)',
    )
    declare_serial_device = DeclareLaunchArgument(
        'serial_device',
        default_value='/dev/ttyUSB0',
        description='Puerto serie de la ESP32 (transporte serial)',
    )
    declare_serial_baudrate = DeclareLaunchArgument(
        'serial_baudrate',
        default_value='115200',
        description='Baudrate del micro-ROS transport serial (debe coincidir con el firmware)',
    )
    declare_udp_port = DeclareLaunchArgument(
        'udp_port',
        default_value='8888',
        description='Puerto UDP del micro-ROS agent (transporte udp4)',
    )

    # ------------------------------------------------------------------
    # Sublaunches
    # ------------------------------------------------------------------
    rplidar_launch = PathJoinSubstitution([
        ThisLaunchFileDir(),
        'rplidar.launch.py',
    ])

    chassis_launch = PathJoinSubstitution([
        ThisLaunchFileDir(),
        'chassis.launch.py',
    ])

    webcam_launch = PathJoinSubstitution([
        ThisLaunchFileDir(),
        'webcam.launch.py',
    ])

    return LaunchDescription([
        declare_chassis_backend,
        declare_microros_transport,
        declare_serial_device,
        declare_serial_baudrate,
        declare_udp_port,

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(rplidar_launch)
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(chassis_launch),
            launch_arguments={
                'chassis_backend': chassis_backend,
                'microros_transport': microros_transport,
                'serial_device': serial_device,
                'serial_baudrate': serial_baudrate,
                'udp_port': udp_port,
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(webcam_launch),
            # El edge solo publica el frame 'laser' (del rplidar), no hay
            # robot_state_publisher con base_link, por eso anclamos la camara
            # al frame 'laser' para mantener el arbol TF conectado.
            launch_arguments={'parent_frame': 'laser'}.items(),
        ),
    ])
