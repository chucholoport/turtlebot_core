#!/usr/bin/env python3

"""
Nodo OpenCV MÍNIMO: convierte la imagen de la cámara a blanco y negro.

    suscribe:  /image_raw        (sensor_msgs/Image, color de la webcam)
    publica:   /image_processed  (sensor_msgs/Image, en escala de grises)

Es el punto de partida del alumno. Todo lo demás —cámara, red ROS 2 y chassis—
ya está conectado: aquí solo escribes TU visión artificial dentro de on_image()
(detectar un color, bordes, seguir una línea...) y decides cómo actuar
publicando en /set_led (encender algo) o /cmd_vel (mover el robot).
"""

import cv2

from cv_bridge import CvBridge

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image


class VisionBW(Node):
    """Convierte /image_raw a blanco y negro y lo republica."""

    def __init__(self):
        super().__init__('vision_bw')

        self.bridge = CvBridge()

        self.sub = self.create_subscription(
            Image, '/image_raw', self.on_image, 10)

        self.pub = self.create_publisher(
            Image, '/image_processed', 10)

        self.get_logger().info(
            'vision_bw listo: /image_raw -> (blanco y negro) -> /image_processed')

    def on_image(self, msg: Image) -> None:
        """Recibe un frame, lo procesa y lo republica."""
        # 1) ROS Image -> OpenCV (BGR)
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # -----------------------------------------------------------------
        #  👇 AQUÍ VA TU CÓDIGO. De fábrica solo pasa a blanco y negro:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # -----------------------------------------------------------------

        # 2) OpenCV (gris) -> ROS Image y publica
        out = self.bridge.cv2_to_imgmsg(gray, encoding='mono8')
        out.header = msg.header          # conserva timestamp y frame_id
        self.pub.publish(out)


def main(args=None):
    """Inicializa ROS 2 y ejecuta el nodo."""
    rclpy.init(args=args)

    node = VisionBW()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
