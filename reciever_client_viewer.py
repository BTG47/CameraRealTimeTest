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

# IP de la computadora Fedora que tiene la cámara.
# Cambia esto por la IP real de Fedora.
CAMERA_SERVER_IP = "140.148.192.26"

# Puerto donde Fedora está escuchando.
CAMERA_SERVER_PORT = 9999


def receive_exactly(sock, num_bytes):
    """
    Recibe exactamente num_bytes desde el socket.
    TCP puede partir los datos en varios paquetes, por eso se acumula.
    """
    data = b""

    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))

        if not packet:
            return None

        data += packet

    return data


class VideoClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cliente receptor de video")

        self.running = True
        self.current_frame = None

        self.frames_received = 0
        self.last_fps_time = time.time()
        self.current_fps = 0.0

        self.video_label = tk.Label(
            root,
            text="Conectando al servidor de cámara...",
            bg="black",
            fg="white",
            width=80,
            height=25
        )
        self.video_label.pack(padx=10, pady=10)

        self.status_label = tk.Label(root, text="Estado: conectando")
        self.status_label.pack(pady=5)

        self.fps_label = tk.Label(root, text="FPS: 0.0")
        self.fps_label.pack(pady=5)

        self.close_button = tk.Button(root, text="Cerrar", command=self.close)
        self.close_button.pack(pady=10)

        self.client_thread = threading.Thread(target=self.connect_and_receive, daemon=True)
        self.client_thread.start()

        self.update_gui()

        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def connect_and_receive(self):
        """
        Ubuntu inicia la conexión hacia Fedora.
        Después recibe los frames enviados por Fedora.
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.set_status(
                f"Estado: conectando a {CAMERA_SERVER_IP}:{CAMERA_SERVER_PORT}"
            )

            client_socket.connect((CAMERA_SERVER_IP, CAMERA_SERVER_PORT))

            self.set_status("Estado: conectado al servidor de cámara")
            print(f"Conectado a {CAMERA_SERVER_IP}:{CAMERA_SERVER_PORT}")

            while self.running:
                size_data = receive_exactly(client_socket, 4)

                if size_data is None:
                    self.set_status("Estado: conexión cerrada por el servidor")
                    break

                frame_size = struct.unpack(">L", size_data)[0]

                frame_data = receive_exactly(client_socket, frame_size)

                if frame_data is None:
                    self.set_status("Estado: conexión cerrada por el servidor")
                    break

                np_data = np.frombuffer(frame_data, dtype=np.uint8)
                frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

                if frame is None:
                    continue

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.current_frame = frame_rgb

                self.frames_received += 1
                self.calculate_fps()

        except ConnectionRefusedError:
            self.set_status("Estado: conexión rechazada. ¿Está abierto camera_server.py en Fedora?")
            print("Conexión rechazada.")

        except TimeoutError:
            self.set_status("Estado: tiempo de conexión agotado")
            print("Tiempo de conexión agotado.")

        except Exception as e:
            self.set_status(f"Estado: error - {e}")
            print(f"Error en cliente receptor: {e}")

        finally:
            client_socket.close()
            print("Cliente cerrado.")

    def calculate_fps(self):
        current_time = time.time()
        elapsed = current_time - self.last_fps_time

        if elapsed >= 1.0:
            self.current_fps = self.frames_received / elapsed
            self.frames_received = 0
            self.last_fps_time = current_time

    def update_gui(self):
        if self.current_frame is not None:
            image = Image.fromarray(self.current_frame)
            photo = ImageTk.PhotoImage(image=image)

            self.video_label.configure(image=photo, text="")
            self.video_label.image = photo

            self.fps_label.configure(text=f"FPS: {self.current_fps:.1f}")

        if self.running:
            self.root.after(15, self.update_gui)

    def set_status(self, text):
        self.root.after(0, lambda: self.status_label.configure(text=text))

    def close(self):
        self.running = False
        self.root.destroy()


def main():
    root = tk.Tk()
    app = VideoClientApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()