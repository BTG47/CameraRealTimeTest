import cv2
import socket
import struct
import time
import numpy as np
import mss

# ============================================================
# CONFIGURACIÓN
# ============================================================

# Escuchar en todas las interfaces de red.
HOST = "0.0.0.0"

# Puerto donde se esperará la conexión del receptor.
PORT = 9999

# Resolución enviada.
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# Calidad JPEG.
JPEG_QUALITY = 85

# Limitar FPS
TARGET_FPS = 60
FRAME_DELAY = 1.0 / TARGET_FPS


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
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Permite reutilizar el puerto si reinicias el programa rápido.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)

        print(f"Servidor de captura escuchando en {HOST}:{PORT}")
        print("Esperando conexión desde la computadora receptora...")

        conn, addr = server_socket.accept()
        print(f"Receptor conectado desde {addr[0]}:{addr[1]}")

        with conn:
            with mss.mss() as sct:
                # monitor 1 suele ser el primario.
                monitor = sct.monitors[1] 
                while True:
                    start_time = time.time()
                    
                    # Capturar la pantalla con mss (excelente rendimiento en X11/Windows/Mac)
                    screen = sct.grab(monitor)
                    
                    # Convertir a numpy array y cambiar de BGRA a BGR (formato de OpenCV)
                    frame = np.array(screen)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

                    ok = send_frame(conn, frame)

                    if not ok:
                        print("Error: no se pudo enviar el frame.")
                        continue

                    # Controlar FPS
                    elapsed = time.time() - start_time
                    if elapsed < FRAME_DELAY:
                        time.sleep(FRAME_DELAY - elapsed)

    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")

    except BrokenPipeError:
        print("El receptor cerró la conexión.")

    except ConnectionResetError:
        print("El receptor reinició la conexión.")

    except Exception as e:
        print(f"Error en servidor de captura: {e}")

    finally:
        server_socket.close()
        print("Servidor cerrado.")


if __name__ == "__main__":
    main()