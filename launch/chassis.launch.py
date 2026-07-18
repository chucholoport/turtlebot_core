from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import (
    EqualsSubstitution,
    LaunchConfiguration,
    PythonExpression,
)
from launch_ros.actions import Node


def generate_launch_description():
    """
    Backend del chassis conmutable segun la plataforma que lo despliegue:

      * uno_q   -> nodo uno_q_bridge (Arduino Uno Q)
      * microros -> micro-ROS agent para la ESP32 (ESP-IDF 5.4), por serial o UDP

    Ejemplos:
      ros2 launch turtlebot_core chassis.launch.py chassis_backend:=uno_q
      ros2 launch turtlebot_core chassis.launch.py chassis_backend:=microros microros_transport:=serial serial_device:=/dev/ttyUSB0
      ros2 launch turtlebot_core chassis.launch.py chassis_backend:=microros microros_transport:=udp4 udp_port:=8888
    """

    # ------------------------------------------------------------------
    # Argumentos
    # ------------------------------------------------------------------
    backend = LaunchConfiguration('chassis_backend')
    microros_transport = LaunchConfiguration('microros_transport')
    serial_device = LaunchConfiguration('serial_device')
    serial_baudrate = LaunchConfiguration('serial_baudrate')
    udp_port = LaunchConfiguration('udp_port')

    declare_backend = DeclareLaunchArgument(
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
    # Backend 1: uno_q_bridge (Arduino Uno Q)
    # ------------------------------------------------------------------
    uno_q_bridge_node = Node(
        name='uno_q_bridge',
        package='uno_q_bridge',
        executable='chassis_bridge',
        output='screen',
        condition=IfCondition(EqualsSubstitution(backend, 'uno_q')),
    )

    # ------------------------------------------------------------------
    # Backend 2: micro-ROS agent (ESP32 / ESP-IDF 5.4)
    #   Se levanta el agente que dialoga con el firmware micro-ROS del MCU.
    #   Serie y UDP van en nodos separados, cada uno con su condicion.
    # ------------------------------------------------------------------
    micro_ros_agent_serial = Node(
        name='micro_ros_agent',
        package='micro_ros_agent',
        executable='micro_ros_agent',
        output='screen',
        arguments=['serial', '--dev', serial_device, '-b', serial_baudrate],
        condition=IfCondition(PythonExpression([
            "'", backend, "' == 'microros' and '", microros_transport, "' == 'serial'",
        ])),
    )

    micro_ros_agent_udp = Node(
        name='micro_ros_agent',
        package='micro_ros_agent',
        executable='micro_ros_agent',
        output='screen',
        arguments=['udp4', '--port', udp_port],
        condition=IfCondition(PythonExpression([
            "'", backend, "' == 'microros' and '", microros_transport, "' == 'udp4'",
        ])),
    )

    return LaunchDescription([
        declare_backend,
        declare_microros_transport,
        declare_serial_device,
        declare_serial_baudrate,
        declare_udp_port,
        uno_q_bridge_node,
        micro_ros_agent_serial,
        micro_ros_agent_udp,
    ])
