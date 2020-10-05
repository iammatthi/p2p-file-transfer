import socket
import sys
import threading
import time

from src.peer import Peer
from src.utils import clear, get_ip


class Receiver(Peer):

    def __init__(self):
        super().__init__()

    def start(self):
        clear()

        ip = get_ip()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((ip, self.port))
        s.listen(5)
        clear()
        print(f'Your are visible as: {self.name} ({ip})')
        while True:
            conn, address = s.accept()
            thread = threading.Thread(
                target=self.handle_sender, args=(conn, address))
            thread.start()

    def handle_sender(self, sender_socket, address):
        msg_type = self.receive_type(conn=sender_socket)

        if msg_type == self.msg_types.get("name"):
            self.send(conn=sender_socket, msg_type=self.msg_types.get(
                "response"), msg=self.name)

        elif msg_type == self.msg_types.get("register"):
            sender_ip = address[0]
            name = "Unknown"

            msg_length = self.receive_length(conn=sender_socket)
            name = self.receive_msg(
                conn=sender_socket, msg_length=msg_length).decode(self.format)
            print(f'\nNew connection with {name} ({sender_ip})')

            buffer = {}
            while True:
                msg_type = self.receive_type(conn=sender_socket)

                if msg_type == self.msg_types.get("disconnect"):
                    print(f'{name} ({sender_ip}) is now disconnected')
                    break

                elif msg_type == self.msg_types.get("file"):
                    filename = buffer["filename"]
                    del buffer["filename"]

                    file_length = self.receive_length(conn=sender_socket)
                    file_bytes = self.receive_msg(
                        conn=sender_socket, msg_length=file_length)

                    f = open(f'downloads/{filename}', 'wb')
                    f.write(file_bytes)
                    f.close()

                    print(f'{name} ({sender_ip}) has sent {filename} to you')

                    self.send(conn=sender_socket, msg_type=self.msg_types.get("response"), msg="success")

                elif msg_type == self.msg_types.get("filename"):
                    filename_length = self.receive_length(conn=sender_socket)
                    filename = self.receive_msg(
                        conn=sender_socket, msg_length=filename_length).decode(self.format)
                    buffer["filename"] = filename

                    print(f'{name} ({sender_ip}) wants to send you {filename}')
                    res = input("Do you want to accept the file (Y/n): ")

                    self.send(conn=sender_socket, msg_type=self.msg_types.get(
                        "response"), msg=res.lower())

                elif msg_type == self.msg_types.get("name"):
                    self.send(conn=sender_socket, msg_type=self.msg_types.get(
                        "response"), msg=self.name)

        sender_socket.close()
