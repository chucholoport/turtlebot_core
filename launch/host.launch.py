import configparser
import os
import tempfile

import yaml

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import LogInfo
from launch.actions import OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


PKG = 'turtlebot_core'


# =====================================================================
#  host.launch.py — visualizacion en la PC (RViz2).
#
#  Arma un rviz/turtlebot.rviz A LA MEDIDA del robot: parte de una escena
#  base (Grid + TF) y le agrega el bloque de cada feature que el robot
#  realmente tiene, leyendo el MISMO robot.ini que usa edge.launch.py:
#
#     [devices] rplidar = true  -> agrega el bloque rplidar.rviz (LaserScan)
#     [devices] webcam  = true  -> agrega el bloque camera.rviz  (Image + Camera)
#
#  Asi RViz solo muestra lo que existe, sin displays "muertos".
#
#  [platform] target = sbc | host:
#    sbc  (default) -> SOLO RViz. La captura corre en la SBC (edge.launch.py),
#                      por red.
#    host           -> pruebas locales en tu PC: ademas de RViz, despliega la
#                      CAPTURA (incluye edge.launch.py). Todo en un comando.
#                      Con video_device:=/dev/video2 apuntas a la webcam del PC.
# =====================================================================

# Features -> bloque .rviz (lista de Displays) que se fusiona en la escena
FEATURE_BLOCKS = [
    ('rplidar', 'rplidar.rviz'),
    ('webcam', 'camera.rviz'),
]


def _load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def _launch_setup(context, *args, **kwargs):
    config_file = LaunchConfiguration('config_file').perform(context)
    video_device = LaunchConfiguration('video_device').perform(context)
    rviz_dir = os.path.join(get_package_share_directory(PKG), 'rviz')
    launch_dir = os.path.join(get_package_share_directory(PKG), 'launch')

    # 1) Escena base (Panels, Global Options, Tools, Views, Grid, TF)
    scene = _load_yaml(os.path.join(rviz_dir, 'base.rviz'))
    displays = scene['Visualization Manager']['Displays']

    # 2) Que tiene el robot -> que bloques agregar
    cfg = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
    cfg.read(config_file)

    target = cfg.get('platform', 'target', fallback='sbc')

    added = []
    for key, fname in FEATURE_BLOCKS:
        if cfg.getboolean('devices', key, fallback=False):
            displays.extend(_load_yaml(os.path.join(rviz_dir, fname)))
            added.append(key)

    # 3) Escribir la escena ensamblada (fallback a /tmp si share es de solo lectura)
    out_path = os.path.join(rviz_dir, 'turtlebot.rviz')
    try:
        with open(out_path, 'w') as f:
            yaml.safe_dump(scene, f, default_flow_style=False, sort_keys=False)
    except OSError:
        out_path = os.path.join(tempfile.gettempdir(), 'turtlebot.rviz')
        with open(out_path, 'w') as f:
            yaml.safe_dump(scene, f, default_flow_style=False, sort_keys=False)

    actions = [
        LogInfo(msg='[host] RViz features: '
                    f'{", ".join(added) if added else "solo base (Grid + TF)"} '
                    f'-> {out_path}'),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', out_path],
        ),
    ]

    # ---- Modo host: pruebas locales -> desplegar tambien la captura ----
    # La captura (edge.launch.py) SOLO se incluye aqui; edge nunca incluye a
    # host, asi que no hay recursion posible.
    if target == 'host':
        actions.append(LogInfo(
            msg='[host] target=host -> incluyo la captura local (edge.launch.py)'))
        actions.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, 'edge.launch.py')),
            launch_arguments={
                'config_file': config_file,
                'video_device': video_device,
            }.items(),
        ))

    return actions


def generate_launch_description():
    default_config = os.path.join(get_package_share_directory(PKG), 'robot.ini')

    return LaunchDescription([
        DeclareLaunchArgument(
            'config_file',
            default_value=default_config,
            description='robot.ini que define que features tiene el robot '
                        '(mismos [devices] que usa edge.launch.py).',
        ),
        DeclareLaunchArgument(
            'video_device',
            default_value='',
            description='Video device de la webcam para la captura en modo host '
                        '(p.ej. /dev/video2). Vacio = usa robot.ini.',
        ),
        OpaqueFunction(function=_launch_setup),
    ])
