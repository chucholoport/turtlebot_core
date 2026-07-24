from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    # ---------------------------------------------------------------------
    # Argumentos configurables (se pueden sobrescribir desde la linea de
    # comandos, p.ej: ros2 launch turtlebot_core webcam.launch.py video_device:=/dev/video2)
    # edge.launch.py los inyecta desde robot.ini.
    # ---------------------------------------------------------------------
    video_device = LaunchConfiguration('video_device')
    pixel_format = LaunchConfiguration('pixel_format')
    image_width = LaunchConfiguration('image_width')
    image_height = LaunchConfiguration('image_height')
    framerate = LaunchConfiguration('framerate')
    parent_frame = LaunchConfiguration('parent_frame')
    camera_frame = LaunchConfiguration('camera_frame')
    optical_frame = LaunchConfiguration('optical_frame')

    declare_video_device = DeclareLaunchArgument(
        'video_device',
        default_value='/dev/video0',
        description='Dispositivo V4L2 de la webcam',
    )
    declare_pixel_format = DeclareLaunchArgument(
        'pixel_format',
        default_value='yuyv',
        description='Formato de pixel: yuyv o mjpeg2rgb (segun la camara)',
    )
    declare_image_width = DeclareLaunchArgument(
        'image_width',
        default_value='640',
        description='Ancho de la imagen en pixeles',
    )
    declare_image_height = DeclareLaunchArgument(
        'image_height',
        default_value='480',
        description='Alto de la imagen en pixeles',
    )
    declare_framerate = DeclareLaunchArgument(
        'framerate',
        default_value='30.0',
        description='Cuadros por segundo',
    )
    declare_parent_frame = DeclareLaunchArgument(
        'parent_frame',
        default_value='base_link',
        # Si visualizas solo con el rplidar, puedes usar 'laser' como parent_frame
        description='Frame padre al que se ancla la camara en el arbol TF',
    )
    declare_camera_frame = DeclareLaunchArgument(
        'camera_frame',
        default_value='camera_link',
        description='Frame fisico de la camara',
    )
    declare_optical_frame = DeclareLaunchArgument(
        'optical_frame',
        default_value='camera_optical_frame',
        description='Frame optico (con el que se publica la imagen)',
    )

    # ---------------------------------------------------------------------
    # Driver de la webcam (paquete usb-cam)
    # La imagen se publica con frame_id = optical_frame para que en RViz2
    # el sensor apunte correctamente (convencion optica REP-103).
    # ---------------------------------------------------------------------
    usb_cam_node = Node(
        name='usb_cam',
        package='usb_cam',
        executable='usb_cam_node_exe',
        output='screen',
        parameters=[{
            'video_device': video_device,
            'frame_id': optical_frame,
            'pixel_format': pixel_format,
            'image_width': ParameterValue(image_width, value_type=int),
            'image_height': ParameterValue(image_height, value_type=int),
            'framerate': ParameterValue(framerate, value_type=float),
            'camera_name': 'webcam',
        }],
    )

    # ---------------------------------------------------------------------
    # Transform 1: parent_frame -> camera_link
    # Posicion fisica de la camara sobre el robot. Ajusta x/y/z segun montaje.
    # args: --x --y --z --roll --pitch --yaw --frame-id --child-frame-id
    # ---------------------------------------------------------------------
    tf_camera_link = Node(
        name='tf_camera_link',
        package='tf2_ros',
        executable='static_transform_publisher',
        output='screen',
        arguments=[
            '--x', '0.10',
            '--y', '0.0',
            '--z', '0.10',
            '--roll', '0.0',
            '--pitch', '0.0',
            '--yaw', '0.0',
            '--frame-id', parent_frame,
            '--child-frame-id', camera_frame,
        ],
    )

    # ---------------------------------------------------------------------
    # Transform 2: camera_link -> camera_optical_frame
    # Rotacion optica (-pi/2, 0, -pi/2) que convierte los ejes ROS (x adelante)
    # a los ejes opticos (z adelante). Necesaria para que la imagen se vea
    # correctamente orientada en el display Camera/Image de RViz2.
    # ---------------------------------------------------------------------
    tf_camera_optical = Node(
        name='tf_camera_optical',
        package='tf2_ros',
        executable='static_transform_publisher',
        output='screen',
        arguments=[
            '--x', '0.0',
            '--y', '0.0',
            '--z', '0.0',
            '--roll', '-1.5707963',
            '--pitch', '0.0',
            '--yaw', '-1.5707963',
            '--frame-id', camera_frame,
            '--child-frame-id', optical_frame,
        ],
    )

    return LaunchDescription([
        declare_video_device,
        declare_pixel_format,
        declare_image_width,
        declare_image_height,
        declare_framerate,
        declare_parent_frame,
        declare_camera_frame,
        declare_optical_frame,
        usb_cam_node,
        tf_camera_link,
        tf_camera_optical,
    ])
