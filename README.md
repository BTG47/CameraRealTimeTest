# Real-Time Screen Streamer

Este proyecto permite transmitir la pantalla en tiempo real de una computadora a otra a través de la red local (TCP) utilizando Python, OpenCV y sockets. Evolucionó desde un proyecto de cámaras web hacia una solución completa para transmisión de escritorio.

## Requisitos y Dependencias

Para ejecutar este código, necesitas instalar lo siguiente:

- Python 3.x
- OpenCV (`pip install opencv-python`)
- NumPy (`pip install numpy`)
- Pillow (`pip install pillow`) - *Para la interfaz gráfica del cliente.*

### Dependencias para el Servidor (Emisor)
Dependiendo de tu sistema operativo y el entorno de escritorio que utilices, el proyecto incluye dos herramientas de captura:

1. **Si usas Linux con Wayland (Hyprland, Gnome Wayland, Sway):**
   - Asegúrate de tener instalado el paquete `grim` en tu sistema (`sudo pacman -S grim` o similar).
   - Utiliza el script: `camera_server.py`.

2. **Si usas Windows, macOS, o Linux con X11:**
   - Instala la librería mss (`pip install mss`).
   - Utiliza el script: `camera_server_mss.py`.

## Estructura del Proyecto

- `reciever_viewer.py`: El script receptor (modo servidor). Escucha un puerto esperando a que el emisor se conecte y muestra el stream recibido.
- `reciever_client_viewer.py`: El script receptor (modo cliente). Inicia la conexión hacia la IP del emisor para visualizar el stream.
- `camera_server.py`: Script emisor de la pantalla optimizado para **Wayland** (usa `grim`).
- `camera_server_mss.py`: Script emisor de la pantalla optimizado para **Windows/macOS/X11** (usa `mss`).
- `sender_camera.py`: Versión antigua y básica del emisor utilizando Pillow `ImageGrab`.

## Cómo usarlo

1. **Inicia el receptor (La computadora que verá la pantalla):**
   Puedes usar `reciever_viewer.py` o `reciever_client_viewer.py`. Asegúrate de abrir el archivo y configurar la IP y el Puerto correcto en la sección de "CONFIGURACIÓN".

2. **Inicia el emisor (La computadora que comparte pantalla):**
   Dependiendo de tu sistema, ejecuta `camera_server.py` o `camera_server_mss.py`.
   *Nota: Por defecto envían la señal a 1280x720 a 60 FPS con calidad JPEG en 85. Esto se puede ajustar dentro de los archivos.*
