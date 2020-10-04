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


def handle_sender(conn, address, name):
    while True:
        # Type
        msg_type = conn.recv(MSG_HEADERS.get("type")).decode(FORMAT)
        if not msg_type:
            continue
        msg_type = msg_type.strip()

        if msg_type == MSG_TYPES.get("disconnect"):
            break
        elif msg_type == MSG_TYPES.get("name"):
            send_msg = name
            send_msg = f'{MSG_TYPES.get("response"):<{MSG_HEADERS.get("type")}}' + f'{len(send_msg):<{MSG_HEADERS.get("length")}}' + send_msg
            conn.send(bytes(send_msg, FORMAT))
            continue
        elif msg_type == MSG_TYPES.get("filename"):
            
            # Length
            msg_length = conn.recv(MSG_HEADERS.get("length")).decode(FORMAT)
            if not msg_length:
                continue
            msg_length = int(msg_length.strip())

            filename = b''
            while True:
                max_length = max(msg_length, 4096)
                filename += conn.recv(max_length)

                msg_length -= max_length
                if msg_length <= 0:
                    break

            filename = filename.decode(FORMAT)

            # Type
            msg_type = conn.recv(MSG_HEADERS.get("type")).decode(FORMAT)
            if not msg_type:
                continue
            msg_type = msg_type.strip()                

            # Length
            msg_length = conn.recv(MSG_HEADERS.get("length")).decode(FORMAT)
            if not msg_length:
                continue
            msg_length = int(msg_length.strip())

            filebytes = b''
            while True:
                max_length = max(msg_length, 4096)
                filebytes += conn.recv(max_length)

                msg_length -= max_length
                if msg_length <= 0:
                    break
                    
            
            f = open(filename, 'wb')
            f.write(filebytes)
            f.close()

            print(f'{filename} received from {address}')

    conn.close()


def start():
    NAME = input("Insert your name: ")
    IP = get_ip()
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver_socket.bind((IP, PORT))
    receiver_socket.listen(5)
    while True:
        conn, address = receiver_socket.accept()
        thread = threading.Thread(target=handle_sender, args=(conn, address, NAME))
        thread.start()


if __name__ == '__main__':
    start()
