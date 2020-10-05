import os
import re
import socket
import time

from config import get_config

MSG_HEADERS = get_config("msg", "headers")
MSG_TYPES = get_config("msg", "types")

PORT = get_config("port")
FORMAT = get_config("format")

NAME = "Matthias"
IP = "192.168.178.23"


def send_file(conn, path):
    """
    Send file
    """
    filename = re.match(r'.*[\\/](?P<filename>.*)',
                        path).groupdict().get("filename")
    send(conn=conn, msg_type=MSG_TYPES.get("filename"), msg=filename)

    file_content = open(path, "rb").read()
    print(f'File length: {len(file_content)}')
    print(f'Size: {os.path.getsize(path)}')
    send_msg = f'{MSG_TYPES.get("file"):<{MSG_HEADERS.get("type")}}' + \
        f'{len(file_content):<{MSG_HEADERS.get("length")}}'
    conn.sendall(bytes(send_msg, FORMAT) + file_content)


def send(conn, msg_type, msg=None):
    """
    Send message
    """
    send_msg = f'{msg_type:<{MSG_HEADERS.get("type")}}'

    if msg:
        send_msg += f'{len(msg):<{MSG_HEADERS.get("length")}}' + msg

    conn.sendall(bytes(send_msg, FORMAT))


def sender():
    path = input("Insert the path of the file you want to send: ")

    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver_socket.connect((IP, PORT))
    send_file(conn=receiver_socket, path=path)


def receiver():
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver_socket.bind((IP, PORT))
    receiver_socket.listen(5)

    conn, address = receiver_socket.accept()

    # - Filename
    # --- Type
    msg_type = conn.recv(MSG_HEADERS.get("type")).decode(FORMAT)
    msg_type = msg_type.strip()

    # --- Length
    filename_length = conn.recv(MSG_HEADERS.get("length")).decode(FORMAT)
    filename_length = int(filename_length.strip())
    print(f'Filename length: {filename_length}')

    # --- Message
    filename_bytes = b''
    remining_filename_length = filename_length
    while True:
        min_length = min(remining_filename_length, 4096)
        downloaded_bytes_length = conn.recv(min_length)

        filename_bytes += downloaded_bytes_length

        remining_filename_length -= len(downloaded_bytes_length)
        if remining_filename_length <= 0:
            break

    filename = filename_bytes.decode(FORMAT)

    print(filename)

    # - File
    # --- Type
    msg_type = conn.recv(MSG_HEADERS.get("type")).decode(FORMAT)
    msg_type = msg_type.strip()

    # --- Length
    file_length = conn.recv(MSG_HEADERS.get("length")).decode(FORMAT)
    file_length = int(file_length.strip())
    print(f'File length: {file_length}')

    # --- Message
    file_bytes = b''
    remining_file_length = file_length
    while True:
        min_length = min(remining_file_length, 4096)
        downloaded_bytes_length = conn.recv(min_length)

        file_bytes += downloaded_bytes_length

        remining_file_length -= len(downloaded_bytes_length)
        if remining_file_length <= 0:
            break

    # - Save file
    file_bytes_length = len(file_bytes)
    print(f'{file_bytes_length} bytes downloaded')
    f = open(filename, 'wb')
    f.write(file_bytes)
    f.close()

    print(f'{filename} received from {address[0]}')


print("1. Receiver")
print("2. Sender")
if input("Choose: ") == "1":
    receiver()
else:
    sender()
