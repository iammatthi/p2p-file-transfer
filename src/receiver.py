import socket
import sys
import threading
import time

from config import get_config

MSG_HEADERS = get_config("msg", "headers")
MSG_TYPES = get_config("msg", "types")

PORT = get_config("port")
FORMAT = get_config("format")


def get_ip():
    """
    Get ip
    """
    ips = socket.gethostbyname_ex(socket.gethostname())[2]
    if len(ips) > 1:
        for i, ip in enumerate(ips):
            print(f"{i+1}. {ip}")

        while True:
            res = input("\nChoose the local ip you want to use: ")

            if res.isdigit() and int(res) >= 1 and int(res) <= len(ips):
                return ips[int(res)-1]
            else:
                print("Invalid input")
    else:
        return ips[0]


def send(conn, msg_type, msg=None):
    """
    Send message
    """
    send_msg = f'{msg_type:<{MSG_HEADERS.get("type")}}'

    if msg:
        send_msg += f'{len(msg):<{MSG_HEADERS.get("length")}}' + msg

    conn.sendall(bytes(send_msg, FORMAT))


def handle_sender(conn, address, name):

    buffer = {}
    while True:
        # Type
        msg_type = conn.recv(MSG_HEADERS.get("type")).decode(FORMAT)
        if not msg_type:
            continue
        msg_type = msg_type.strip()

        if msg_type == MSG_TYPES.get("disconnect"):
            break
        elif msg_type == MSG_TYPES.get("name"):
            send(conn=conn, msg_type=MSG_TYPES.get("response"), msg=name)
            continue
        elif msg_type == MSG_TYPES.get("filename"):
            # Length
            filename_length = conn.recv(
                MSG_HEADERS.get("length")).decode(FORMAT)
            if not filename_length:
                continue
            filename_length = int(filename_length.strip())

            filename_bytes = b''
            remining_filename_length = filename_length
            while True:
                min_length = min(remining_filename_length, 4096)
                downloaded_bytes_length = conn.recv(min_length)

                filename_bytes += downloaded_bytes_length

                remining_filename_length -= len(downloaded_bytes_length)
                if remining_filename_length <= 0:
                    break

            buffer["filename"] = filename_bytes.decode(FORMAT)

            continue
        elif msg_type == MSG_TYPES.get("file"):
            # Length
            file_length = conn.recv(MSG_HEADERS.get("length")).decode(FORMAT)
            if not file_length:
                continue
            file_length = int(file_length.strip())

            file_bytes = b''
            remining_file_length = file_length
            while True:
                min_length = min(remining_file_length, 4096)
                downloaded_bytes_length = conn.recv(min_length)

                file_bytes += downloaded_bytes_length

                remining_file_length -= len(downloaded_bytes_length)
                if remining_file_length <= 0:
                    break

            filename = buffer["filename"]
            del buffer["filename"]

            f = open(filename, 'wb')
            f.write(file_bytes)
            f.close()

            print(f'{filename} received from {address[0]}')

            continue

    conn.close()


def start():
    NAME = input("Insert your name: ")
    IP = get_ip()
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver_socket.bind((IP, PORT))
    receiver_socket.listen(5)
    while True:
        conn, address = receiver_socket.accept()
        thread = threading.Thread(
            target=handle_sender, args=(conn, address, NAME))
        thread.start()


if __name__ == '__main__':
    start()
