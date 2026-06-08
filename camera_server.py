import cv2
import socket
import struct
import time


# ============================================================
# CONFIGURACIÓN
# ============================================================

# Escuchar en todas las interfaces de red de Fedora.
HOST = "0.0.0.0"

# Puerto donde Fedora esperará la conexión del receptor.
PORT = 9999

# Cámara de Fedora.
CAMERA_INDEX = 0

# Resolución enviada.
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Calidad JPEG.
JPEG_QUALITY = 70

# Pausa entre frames.
FRAME_DELAY = 0.01


def send_frame(conn, frame):
    """
    Comprime un frame como JPEG y lo envía por TCP.
    Primero manda 4 bytes con el tamaño del frame.
    Luego manda el frame completo.
    """
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
    success, encoded_frame = cv2.imencode(".jpg", frame, encode_params)

    if not success:
        return False

    frame_bytes = encoded_frame.tobytes()
    frame_size = len(frame_bytes)

    conn.sendall(struct.pack(">L", frame_size))
    conn.sendall(frame_bytes)

    return True


def main():
    camera = cv2.VideoCapture(CAMERA_INDEX)

    if not camera.isOpened():
        print("Error: no se pudo abrir la cámara.")
        return

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Permite reutilizar el puerto si reinicias el programa rápido.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)

        print(f"Servidor de cámara escuchando en {HOST}:{PORT}")
        print("Esperando conexión desde la computadora receptora...")

        conn, addr = server_socket.accept()
        print(f"Receptor conectado desde {addr[0]}:{addr[1]}")

        with conn:
            while True:
                ret, frame = camera.read()

                if not ret:
                    print("Error: no se pudo leer frame de la cámara.")
                    break

                frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

                ok = send_frame(conn, frame)

                if not ok:
                    print("Error: no se pudo enviar el frame.")
                    continue

                time.sleep(FRAME_DELAY)

    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")

    except BrokenPipeError:
        print("El receptor cerró la conexión.")

    except ConnectionResetError:
        print("El receptor reinició la conexión.")

    except Exception as e:
        print(f"Error en servidor de cámara: {e}")

    finally:
        camera.release()
        server_socket.close()
        print("Cámara y servidor cerrados.")


if __name__ == "__main__":
    main()