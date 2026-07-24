import configparser
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import LogInfo
from launch.actions import OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


PKG = 'turtlebot_core'


# =====================================================================
#  Launch del edge (el que corre EN el robot: SBC / Raspberry / Uno Q).
#
#  No lleva parametros a mano: lee robot.ini y despliega UNICAMENTE los
#  dispositivos que el alumno marco como conectados. Asi el mismo launch
#  sirve para cualquier robot; lo unico que cambia es robot.ini.
#
#  Este launch SOLO capta. Para pruebas locales en tu PC (robot.ini
#  [platform] target = host) NO lo lanzas tu directamente: lo incluye
#  host.launch.py, que ademas abre RViz. Ahi vive la logica "todo local".
#
#  Para apuntar a otro archivo:
#    ros2 launch turtlebot_core edge.launch.py config_file:=/ruta/otro.ini
# =====================================================================


def _launch_setup(context, *args, **kwargs):
    config_file = LaunchConfiguration('config_file').perform(context)

    cfg = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
    if not cfg.read(config_file):
        return [LogInfo(
            msg='[edge] No se encontro el archivo de configuracion: '
                f'{config_file}. Nada que desplegar.')]

    def get(section, key, default):
        return cfg.get(section, key, fallback=default)

    def enabled(key):
        return cfg.getboolean('devices', key, fallback=False)

    launch_dir = os.path.join(get_package_share_directory(PKG), 'launch')

    def include(name, launch_arguments):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, name)),
            launch_arguments=launch_arguments.items(),
        )

    backend = get('platform', 'backend', 'microros')
    # Override opcional del video_device (util en pruebas host, p.ej. /dev/video2).
    # Vacio => usa el valor de robot.ini [webcam]. host.launch.py lo reenvia aqui.
    video_override = LaunchConfiguration('video_device').perform(context)

    actions = [LogInfo(
        msg=f'[edge] plataforma={backend}  '
            f'rplidar={enabled("rplidar")}  '
            f'webcam={enabled("webcam")}  '
            f'chassis={enabled("chassis")}')]

    # ---- RPLidar ----
    if enabled('rplidar'):
        actions.append(include('rplidar.launch.py', {
            'serial_port': get('rplidar', 'serial_port', '/dev/rplidar'),
            'serial_baudrate': get('rplidar', 'serial_baudrate', '115200'),
            'frame_id': get('rplidar', 'frame_id', 'laser'),
        }))

    # ---- Webcam (usb_cam) ----
    if enabled('webcam'):
        actions.append(include('webcam.launch.py', {
            'video_device': video_override or get('webcam', 'video_device', '/dev/video0'),
            'pixel_format': get('webcam', 'pixel_format', 'yuyv'),
            'image_width': get('webcam', 'image_width', '640'),
            'image_height': get('webcam', 'image_height', '480'),
            'framerate': get('webcam', 'framerate', '30.0'),
            # El edge no publica base_link; anclamos la camara al frame del rplidar
            'parent_frame': get('webcam', 'parent_frame', 'laser'),
        }))

    # ---- MCU / chassis (backend segun la plataforma) ----
    if enabled('chassis'):
        actions.append(include('mcu.launch.py', {
            'backend': backend,
            'firmware': get('platform', 'firmware', 'led'),
            'microros_transport': get('microros', 'transport', 'serial'),
            'serial_device': get('microros', 'serial_device', '/dev/ttyUSB0'),
            'serial_baudrate': get('microros', 'serial_baudrate', '115200'),
            'udp_port': get('microros', 'udp_port', '8888'),
        }))

    return actions


def generate_launch_description():
    default_config = os.path.join(get_package_share_directory(PKG), 'robot.ini')

    return LaunchDescription([
        DeclareLaunchArgument(
            'config_file',
            default_value=default_config,
            description='Archivo .ini con la configuracion del robot '
                        '(plataforma y dispositivos conectados). '
                        'Por defecto: robot.ini del paquete. Edita ese archivo.',
        ),
        DeclareLaunchArgument(
            'video_device',
            default_value='',
            description='Sobrescribe el video_device de la webcam (util en pruebas '
                        'host, p.ej. /dev/video2). Vacio = usa robot.ini.',
        ),
        OpaqueFunction(function=_launch_setup),
    ])
