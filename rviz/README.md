# Visualizar la webcam en RViz2

Guía para configurar RViz2 y ver la imagen de la webcam (paquete `usb_cam`) junto
con el lidar, usando la transform que conecta la cámara al árbol de TF.

## 1. Contexto

`webcam.launch.py` levanta tres cosas:

- **`usb_cam`** → publica la imagen en `/image_raw` (y `/camera_info`) con
  `frame_id = camera_optical_frame`.
- **TF `parent_frame → camera_link`** → posición física de la cámara.
- **TF `camera_link → camera_optical_frame`** → rotación óptica (REP-103) para que
  la imagen quede bien orientada en el display *Camera*.

Sin esas transforms, RViz2 no encuentra el frame de la imagen en el árbol de TF y
no la puede ubicar en la escena 3D.

> El `frame` padre por defecto es `base_link`. Cuando se lanza desde
> `turtlebot_edge.launch.py`, se pasa `parent_frame:=laser` para que el árbol de
> TF quede conectado (`laser → camera_link → camera_optical_frame`).

## 2. Lanzar

Solo la cámara + transforms:

```bash
ros2 launch turtlebot_core webcam.launch.py
```

Con overrides frecuentes:

```bash
# otra cámara
ros2 launch turtlebot_core webcam.launch.py video_device:=/dev/video2

# anclarla al frame del lidar
ros2 launch turtlebot_core webcam.launch.py parent_frame:=laser
```

Todo el edge (lidar + chassis + cámara + TFs):

```bash
ros2 launch turtlebot_core turtlebot_edge.launch.py
```

## 3. Abrir RViz2 con la config lista

Ya existe una configuración pre-armada (`view_camera.rviz`):

```bash
rviz2 -d $(ros2 pkg prefix turtlebot_core)/share/turtlebot_core/rviz/view_camera.rviz
```

Incluye, con **Fixed Frame `laser`**:

| Display | Topic | Estado |
|---|---|---|
| Grid | — | on |
| LaserScan | `scan` | on |
| **Image** | `/image_raw` | on (panel 2D del video) |
| **Camera** | `/image_raw` | off (overlay 3D; usa TF + `/camera_info`) |
| TF | — | on (para ver los frames) |

## 4. Configurarlo a mano (desde cero)

Si arrancas un RViz2 en blanco:

1. **Global Options → Fixed Frame** = `laser` (o `base_link` si no usas lidar).
2. **Add → Image** → *Topic* = `/image_raw`. Es un panel 2D, muestra el video
   directo (no requiere TF).
3. **Add → TF** → deberías ver la cadena
   `laser → camera_link → camera_optical_frame`. Si no aparece completa, la
   transform no está corriendo (ver Troubleshooting).
4. (Opcional) **Add → Camera** → *Topic* = `/image_raw`. Proyecta la imagen en la
   escena 3D; necesita TF válido y `/camera_info`.
5. **File → Save Config As** para guardar tu propio `.rviz`.

## 5. Verificar que todo publica

```bash
ros2 topic hz /image_raw          # debe haber ~30 Hz
ros2 topic list | grep image      # /image_raw, /camera_info
ros2 run tf2_tools view_frames    # genera un PDF del árbol de TF
ros2 run tf2_ros tf2_echo laser camera_optical_frame
```

## 6. Troubleshooting

| Síntoma | Causa probable | Solución |
|---|---|---|
| El display *Image* está vacío | La cámara no publica | `ros2 topic hz /image_raw`; revisa `video_device` |
| Error de formato al abrir la cámara | `pixel_format` no soportado | `v4l2-ctl --device=/dev/video0 --list-formats-ext` y ajusta `pixel_format` (p. ej. `mjpeg2rgb`) en `webcam.launch.py` |
| *Camera* dice "No TF" / frame desconectado | El `parent_frame` no está en el árbol | Lanza con `parent_frame:=laser` (o el frame que exista) |
| No hay `/dev/video0` en el contenedor | Falta exponer el dispositivo | El `docker-compose.yml` ya monta `/dev`; verifica que la webcam esté conectada al host |
| La imagen se ve rotada/espejada en 3D | Falta el frame óptico | Confirma que corre el TF `camera_link → camera_optical_frame` |
