import socket
import struct
import threading
import time
import tkinter as tk

import cv2
import numpy as np
from PIL import Image, ImageTk


# ============================================================
# CONFIGURACIÓN
# ============================================================

# Escucha en todas las interfaces de red.
# Déjalo así para que acepte conexiones desde otra computadora.
HOST = "0.0.0.0"

# Debe coincidir con el puerto del sender_camera.py
PORT = 9999


def receive_exactly(sock, num_bytes):
    """
    Recibe exactamente num_bytes desde el socket.
    TCP no garantiza que todo llegue en una sola llamada a recv,
    por eso acumulamos hasta tener la cantidad completa.
    """
    data = b""

    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))

        if not packet:
            return None

        data += packet

    return data


class VideoReceiverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Receptor de video")

        self.running = True
        self.current_frame = None

        self.frames_received = 0
        self.last_fps_time = time.time()
        self.current_fps = 0.0

        # =====================================================
        # INTERFAZ
        # =====================================================

        self.video_label = tk.Label(root, text="Esperando conexión...", bg="black", fg="white")
        self.video_label.pack(padx=10, pady=10)

        self.status_label = tk.Label(root, text="Estado: esperando conexión")
        self.status_label.pack(pady=5)

        self.fps_label = tk.Label(root, text="FPS: 0.0")
        self.fps_label.pack(pady=5)

        self.close_button = tk.Button(root, text="Cerrar", command=self.close)
        self.close_button.pack(pady=10)

        # Iniciar hilo de recepción
        self.receiver_thread = threading.Thread(target=self.start_server, daemon=True)
        self.receiver_thread.start()

        # Actualizar interfaz
        self.update_gui()

        # Manejar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def start_server(self):
        """
        Crea el servidor TCP y espera al emisor.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Permite reutilizar el puerto si cerraste y abriste rápido el programa.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server_socket.bind((HOST, PORT))
            server_socket.listen(1)

            self.set_status(f"Estado: esperando conexión en puerto {PORT}")
            print(f"Servidor escuchando en {HOST}:{PORT}")

            conn, addr = server_socket.accept()
            self.set_status(f"Estado: conectado desde {addr[0]}")
            print(f"Conectado desde {addr}")

            with conn:
                while self.running:
                    # Leer los primeros 4 bytes: tamaño del frame
                    size_data = receive_exactly(conn, 4)

                    if size_data is None:
                        self.set_status("Estado: conexión cerrada")
                        break

                    frame_size = struct.unpack(">L", size_data)[0]

                    # Leer el frame completo
                    frame_data = receive_exactly(conn, frame_size)

                    if frame_data is None:
                        self.set_status("Estado: conexión cerrada")
                        break

                    # Convertir bytes JPEG a imagen OpenCV
                    np_data = np.frombuffer(frame_data, dtype=np.uint8)
                    frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

                    if frame is None:
                        continue

                    # OpenCV usa BGR, Tkinter/Pillow usa RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    self.current_frame = frame_rgb
                    self.frames_received += 1

                    self.calculate_fps()

        except Exception as e:
            self.set_status(f"Estado: error - {e}")
            print(f"Error en servidor: {e}")

        finally:
            server_socket.close()
            print("Servidor cerrado.")

    def calculate_fps(self):
        """
        Calcula FPS aproximados.
        """
        current_time = time.time()
        elapsed = current_time - self.last_fps_time

        if elapsed >= 1.0:
            self.current_fps = self.frames_received / elapsed
            self.frames_received = 0
            self.last_fps_time = current_time

    def update_gui(self):
        """
        Actualiza la imagen en la interfaz.
        """
        if self.current_frame is not None:
            image = Image.fromarray(self.current_frame)
            photo = ImageTk.PhotoImage(image=image)

            self.video_label.configure(image=photo, text="")
            self.video_label.image = photo

            self.fps_label.configure(text=f"FPS: {self.current_fps:.1f}")

        if self.running:
            self.root.after(15, self.update_gui)

    def set_status(self, text):
        """
        Actualiza el texto de estado desde cualquier hilo.
        """
        self.root.after(0, lambda: self.status_label.configure(text=text))

    def close(self):
        """
        Cierra la aplicación.
        """
        self.running = False
        self.root.destroy()


def main():
    root = tk.Tk()
    app = VideoReceiverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()