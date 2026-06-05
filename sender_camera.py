import cv2
import socket
import struct
import time


# ============================================================
# CONFIGURACIÓN
# ============================================================

# IP de la computadora que recibirá el video.
# Cambia esto por la IP local de la computadora receptora.
RECEIVER_IP = "192.168.1.75"

# Puerto que usará el receptor.
RECEIVER_PORT = 9999

# Índice de cámara:
# 0 normalmente es la cámara integrada o la primera cámara USB.
CAMERA_INDEX = 0

# Resolución del video enviado.
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Calidad JPEG:
# Más alto = mejor imagen, más peso, más latencia.
# Recomendado: 60 a 80.
JPEG_QUALITY = 70

# Pequeña pausa para no saturar demasiado la red.
# Puedes poner 0 si quieres máxima velocidad.
FRAME_DELAY = 0.01


def connect_to_receiver():
    """
    Intenta conectarse a la computadora receptora.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"Conectando a {RECEIVER_IP}:{RECEIVER_PORT}...")
    client_socket.connect((RECEIVER_IP, RECEIVER_PORT))
    print("Conectado al receptor.")

    return client_socket


def main():
    # Abrir cámara
    camera = cv2.VideoCapture(CAMERA_INDEX)

    if not camera.isOpened():
        print("Error: no se pudo abrir la cámara.")
        return

    # Configurar resolución de captura
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    # Conectar al receptor
    try:
        client_socket = connect_to_receiver()
    except Exception as e:
        print(f"Error al conectar con el receptor: {e}")
        camera.release()
        return

    try:
        while True:
            ret, frame = camera.read()

            if not ret:
                print("Error: no se pudo leer frame de la cámara.")
                break

            # Redimensionar por seguridad
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

            # Comprimir frame a JPEG
            encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
            success, encoded_frame = cv2.imencode(".jpg", frame, encode_params)

            if not success:
                print("Error: no se pudo comprimir el frame.")
                continue

            frame_bytes = encoded_frame.tobytes()

            # Enviar primero el tamaño del frame.
            # struct.pack(">L", tamaño) usa 4 bytes en big-endian.
            frame_size = len(frame_bytes)
            client_socket.sendall(struct.pack(">L", frame_size))

            # Enviar los bytes del frame
            client_socket.sendall(frame_bytes)

            time.sleep(FRAME_DELAY)

    except KeyboardInterrupt:
        print("\nTransmisión detenida por el usuario.")

    except Exception as e:
        print(f"Error durante la transmisión: {e}")

    finally:
        camera.release()
        client_socket.close()
        print("Cámara y conexión cerradas.")


if __name__ == "__main__":
    main()