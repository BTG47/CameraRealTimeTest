# Camera Stream TCP con Python

Este proyecto permite transmitir video en tiempo real desde la cámara de una computadora hacia otra computadora dentro de la misma red local.

El sistema se divide en dos programas:

- `sender_camera.py`: se ejecuta en la computadora que tiene la cámara.
- `receiver_viewer.py`: se ejecuta en la computadora que recibirá y mostrará el video.

La transmisión se realiza usando sockets TCP. Cada frame de la cámara se comprime como imagen JPEG y se envía por red al receptor.

---

## 1. Requisitos

Se necesita tener instalado:

- Anaconda o Miniconda
- Python 3.11
- Cámara integrada o USB en la computadora emisora
- Ambas computadoras conectadas a la misma red local

---

## 2. Crear el entorno con Anaconda

En ambas computadoras, abrir una terminal y ejecutar:

```bash
conda create -n camera_stream python=3.11
```

Activar el entorno:

```bash
conda activate camera_stream
```

Instalar las dependencias:

```bash
pip install opencv-python pillow numpy
```

Este proceso debe hacerse tanto en la computadora emisora como en la computadora receptora.

---

## 3. Archivos del proyecto

El proyecto debe tener al menos estos dos archivos:

```text
camera-stream/
├── sender_camera.py
└── receiver_viewer.py
```

---

## 4. Descripción general del flujo

```text
Computadora con cámara
sender_camera.py
        |
        | Captura frames con OpenCV
        | Comprime cada frame como JPEG
        | Envía los bytes por TCP
        v
Red local
        |
        v
Computadora receptora
receiver_viewer.py
        |
        | Recibe bytes
        | Reconstruye imagen JPEG
        | Muestra video en interfaz Tkinter
```

---

## 5. Conocer la IP de la computadora receptora

Antes de ejecutar el emisor, es necesario conocer la IP local de la computadora que recibirá el video.

### En Windows

Abrir PowerShell o CMD y ejecutar:

```bash
ipconfig
```

Buscar una sección parecida a:

```text
Adaptador de LAN inalámbrica Wi-Fi:

   Dirección IPv4 . . . . . . . . . . . . . : 192.168.1.75
```

La IP que se debe usar es la dirección IPv4, por ejemplo:

```text
192.168.1.75
```

### En Linux

Abrir una terminal y ejecutar:

```bash
hostname -I
```

También se puede usar:

```bash
ip addr
```

Buscar una IP parecida a:

```text
192.168.1.75
```

### En macOS

Abrir una terminal y ejecutar:

```bash
ifconfig
```

También se puede revisar desde:

```text
Configuración del sistema > Red > Wi-Fi > Detalles
```

---

## 6. Configurar el emisor

En la computadora que tiene la cámara, abrir el archivo `sender_camera.py`.

Buscar esta línea:

```python
RECEIVER_IP = "192.168.1.75"
```

Cambiarla por la IP real de la computadora receptora.

Ejemplo:

```python
RECEIVER_IP = "192.168.0.23"
```

También verificar que el puerto sea el mismo en ambos archivos:

```python
RECEIVER_PORT = 9999
```

En `receiver_viewer.py` debe coincidir con:

```python
PORT = 9999
```

---

## 7. Ejecutar el receptor

Primero se debe ejecutar el programa receptor.

En la computadora que recibirá el video:

```bash
conda activate camera_stream
python receiver_viewer.py
```

Se abrirá una ventana con un mensaje parecido a:

```text
Esperando conexión...
```

Es importante ejecutar primero el receptor porque el emisor intentará conectarse a él.

---

## 8. Ejecutar el emisor

Después, en la computadora que tiene la cámara:

```bash
conda activate camera_stream
python sender_camera.py
```

Si la conexión es correcta, la computadora receptora empezará a mostrar el video recibido.

---

## 9. Verificar que ambas computadoras estén en la misma red

Ambas computadoras deben estar conectadas a la misma red local.

Por ejemplo:

```text
Computadora receptora: 192.168.1.75
Computadora emisora:   192.168.1.34
```

Normalmente, si las primeras tres partes de la IP coinciden, están en la misma red:

```text
192.168.1.xxx
```

Si una computadora tiene una IP como:

```text
192.168.1.75
```

y la otra tiene:

```text
10.0.0.15
```

puede que estén en redes diferentes.

---

## 10. Probar conexión con ping

Desde la computadora emisora, se puede probar si alcanza a ver a la computadora receptora.

Ejemplo:

```bash
ping 192.168.1.75
```

Si responde, debería aparecer algo parecido a:

```text
Reply from 192.168.1.75: bytes=32 time=3ms TTL=64
```

En Linux/macOS puede aparecer algo como:

```text
64 bytes from 192.168.1.75: icmp_seq=1 ttl=64 time=3.2 ms
```

Si no responde, revisar:

- Que ambas computadoras estén en la misma red.
- Que el firewall no esté bloqueando la conexión.
- Que la IP configurada sea correcta.
- Que el receptor esté ejecutándose antes que el emisor.

---

## 11. Firewall

En Windows puede aparecer una alerta de seguridad al ejecutar Python.

Se debe permitir el acceso en redes privadas.

Si no aparece la alerta y no conecta, revisar manualmente:

```text
Configuración > Seguridad de Windows > Firewall y protección de red
```

Permitir Python en redes privadas puede ser necesario.

En Linux, si se usa firewall, puede abrirse el puerto 9999.

Ejemplo con `ufw`:

```bash
sudo ufw allow 9999/tcp
```

---

## 12. Ajustar calidad y latencia

En `sender_camera.py` se pueden ajustar estos valores:

```python
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
JPEG_QUALITY = 70
FRAME_DELAY = 0.01
```

### Mayor fluidez

Reducir resolución:

```python
FRAME_WIDTH = 320
FRAME_HEIGHT = 240
```

Bajar calidad JPEG:

```python
JPEG_QUALITY = 50
```

Reducir pausa entre frames:

```python
FRAME_DELAY = 0
```

### Mejor calidad de imagen

Subir resolución:

```python
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
```

Subir calidad JPEG:

```python
JPEG_QUALITY = 85
```

Esto puede aumentar la latencia y el consumo de red.

---

## 13. Configuración recomendada para primera prueba

Para probar por primera vez se recomienda:

```python
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
JPEG_QUALITY = 70
FRAME_DELAY = 0.01
```

Esta configuración busca un equilibrio entre calidad, fluidez y baja latencia.

---

## 14. Problemas comunes

### El receptor se queda en “Esperando conexión”

Posibles causas:

- El emisor no se ha ejecutado.
- La IP en `sender_camera.py` es incorrecta.
- El firewall bloquea el puerto.
- Las computadoras no están en la misma red.

---

### El emisor muestra error de conexión

Revisar que el receptor esté abierto antes de ejecutar el emisor.

También revisar que esta línea tenga la IP correcta:

```python
RECEIVER_IP = "IP_DE_LA_COMPUTADORA_RECEPTORA"
```

---

### No se abre la cámara

Cambiar el índice de cámara en `sender_camera.py`:

```python
CAMERA_INDEX = 0
```

Probar con:

```python
CAMERA_INDEX = 1
```

o:

```python
CAMERA_INDEX = 2
```

Esto puede pasar si hay varias cámaras conectadas.

---

### El video se ve lento

Reducir resolución:

```python
FRAME_WIDTH = 320
FRAME_HEIGHT = 240
```

Reducir calidad:

```python
JPEG_QUALITY = 50
```

---

### El video se ve con mucha latencia

Posibles soluciones:

- Usar Ethernet en lugar de Wi-Fi.
- Bajar resolución.
- Bajar calidad JPEG.
- Cerrar programas que consuman red.
- Reducir `FRAME_DELAY`.

---

## 15. Orden correcto de ejecución

El orden correcto siempre es:

```text
1. Ejecutar receiver_viewer.py en la computadora receptora.
2. Ejecutar sender_camera.py en la computadora con cámara.
```

Ejemplo:

### Computadora receptora

```bash
conda activate camera_stream
python receiver_viewer.py
```

### Computadora emisora

```bash
conda activate camera_stream
python sender_camera.py
```

---

## 16. Notas importantes

Este proyecto es una versión inicial para pruebas locales.

Para una versión más avanzada de baja latencia se podría migrar a:

- UDP
- RTP
- FFmpeg
- GStreamer
- H.264/H.265
- WebRTC

La versión actual usa TCP y JPEG porque es más sencilla de entender, probar y modificar.
