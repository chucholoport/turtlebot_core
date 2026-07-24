from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import LogInfo
from launch.conditions import IfCondition
from launch.substitutions import (
    LaunchConfiguration,
    PythonExpression,
)
from launch_ros.actions import Node


def generate_launch_description():
    """
    Puente ROS 2 <-> microcontrolador (MCU) del robot, conmutable segun la placa.

    Pensado para que integres de forma MODULAR tu sketch de Arduino o tu proyecto
    de ESP-IDF, sin tocar el resto del sistema. Dos ejes:

      backend  -> con que placa se habla:
        * uno_q    -> nodo puente uno_q_bridge (Arduino Uno Q, socket UNIX)
        * microros -> micro-ROS agent para la ESP32 (ESP-IDF 5.4), serial o UDP

      firmware -> que variante flasheaste (homonima al firmware/proyecto):
        * led     -> solo LED  (sketch led.ino     / proyecto esp32_ws/led)
        * chassis -> ruedas    (sketch chassis.ino / proyecto esp32_ws/chassis)

    Ejemplos:
      ros2 launch turtlebot_core mcu.launch.py backend:=uno_q firmware:=led
      ros2 launch turtlebot_core mcu.launch.py backend:=uno_q firmware:=chassis
      ros2 launch turtlebot_core mcu.launch.py backend:=microros microros_transport:=serial serial_device:=/dev/ttyUSB0
      ros2 launch turtlebot_core mcu.launch.py backend:=microros microros_transport:=udp4 udp_port:=8888
    """

    # ------------------------------------------------------------------
    # Argumentos
    # ------------------------------------------------------------------
    backend = LaunchConfiguration('backend')
    firmware = LaunchConfiguration('firmware')
    microros_transport = LaunchConfiguration('microros_transport')
    serial_device = LaunchConfiguration('serial_device')
    serial_baudrate = LaunchConfiguration('serial_baudrate')
    udp_port = LaunchConfiguration('udp_port')

    declare_backend = DeclareLaunchArgument(
        'backend',
        default_value='uno_q',
        choices=['uno_q', 'microros'],
        description='Placa con la que se habla: "uno_q" (uno_q_bridge) o '
                    '"microros" (micro-ROS agent para ESP32 con ESP-IDF 5.4)',
    )
    declare_firmware = DeclareLaunchArgument(
        'firmware',
        default_value='led',
        choices=['led', 'chassis'],
        description='Variante flasheada (led / chassis). En uno_q elige el nodo: '
                    'led -> uno_q_bridge (sketch led.ino), chassis -> chassis_bridge '
                    '(sketch chassis.ino). En microros no cambia el agente: debe '
                    'coincidir con el proyecto flasheado (esp32_ws/led o '
                    'esp32_ws/chassis).',
    )
    declare_microros_transport = DeclareLaunchArgument(
        'microros_transport',
        default_value='serial',
        choices=['serial', 'udp4'],
        description='Transporte del micro-ROS agent (solo aplica si backend:=microros)',
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
    # Backend 1: Arduino Uno Q — el nodo depende del firmware flasheado
    #   led.ino     -> nodo uno_q_bridge  (RPC set_led_state, /set_led)
    #   chassis.ino -> nodo chassis_bridge (RPC set_cmd_vel, /cmd_vel)
    # ------------------------------------------------------------------
    uno_q_led_node = Node(
        name='uno_q_bridge',
        package='uno_q_bridge',
        executable='uno_q_bridge',
        output='screen',
        condition=IfCondition(PythonExpression([
            "'", backend, "' == 'uno_q' and '", firmware, "' == 'led'",
        ])),
    )

    uno_q_chassis_node = Node(
        name='uno_q_bridge',
        package='uno_q_bridge',
        executable='chassis_bridge',
        output='screen',
        condition=IfCondition(PythonExpression([
            "'", backend, "' == 'uno_q' and '", firmware, "' == 'chassis'",
        ])),
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

    # En microros el agente es el mismo para led/chassis: la variante vive en el
    # PROYECTO que flasheaste (esp32_ws/led o esp32_ws/chassis). Aqui 'firmware'
    # no cambia el agente; dejamos un recordatorio para que el firmware
    # flasheado coincida.
    microros_firmware_reminder = LogInfo(
        msg=['[mcu] backend=microros, firmware="', firmware,
             '": flashea el proyecto que corresponda '
             '(led -> esp32_ws/led, chassis -> esp32_ws/chassis). '
             'El firmware no cambia el agente.'],
        condition=IfCondition(PythonExpression([
            "'", backend, "' == 'microros'",
        ])),
    )

    return LaunchDescription([
        declare_backend,
        declare_firmware,
        declare_microros_transport,
        declare_serial_device,
        declare_serial_baudrate,
        declare_udp_port,
        uno_q_led_node,
        uno_q_chassis_node,
        micro_ros_agent_serial,
        micro_ros_agent_udp,
        microros_firmware_reminder,
    ])
