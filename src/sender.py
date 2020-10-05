import re
import socket
import sys
import time

from config import get_config
from tqdm import tqdm


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
                return ips[int(res) - 1]
            else:
                print("Invalid input")
    else:
        return ips[0]


def get_network_ips(ip):
    """
    Get network
    """
    ip_networks = re.match(
        r'(?P<small>(?P<wide>\d{1,3}\.\d{1,3})\.\d{1,3})\.\d{1,3}', ip).groupdict()
    print(f"1. {ip_networks.get('wide')}.0.0 (not supported yet)")
    print(f"2. {ip_networks.get('small')}.0")

    while True:
        res = input("\nChoose your network: ")

        if res.isdigit() and int(res) >= 1 and int(res) <= 2:
            if int(res) == 1:
                print("Not supported yet")
                continue

                # network = ip_networks.get('wide')
                # network_ips = []
                # for ip_host_1 in range(0, 256):
                #     for ip_host_2 in range(0, 256):
                #         network_ips.append(f"{network}.{ip_host_1}.{ip_host_2}")
            else:
                network = ip_networks.get('small')
                return [f"{network}.{ip_host}" for ip_host in range(0, 256)]
            break
        else:
            print("Invalid input")


def get_available_receivers(network_ips):
    """
    Get available receivers
    """
    print("Checking available receivers...")
    available_receivers = []
    for ip in tqdm(network_ips):
        receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(0.1)

        result = receiver_socket.connect_ex((ip, PORT))
        if result == 0:
            send(conn=receiver_socket, msg_type=MSG_TYPES.get("name"))

            # Type
            msg_type = receiver_socket.recv(
                MSG_HEADERS.get("type")).decode(FORMAT)
            if not msg_type:
                continue
            msg_type = msg_type.strip()

            # Length
            msg_length = receiver_socket.recv(
                MSG_HEADERS.get("length")).decode(FORMAT)
            if not msg_length:
                continue
            msg_length = int(msg_length.strip())

            # Message
            msg = b''
            while True:
                max_length = max(msg_length, 4096)
                msg += receiver_socket.recv(max_length)
                msg_length -= max_length

                if msg_length <= 0:
                    break

            send(conn=receiver_socket, msg_type=MSG_TYPES.get("disconnect"))

            available_receivers.append({
                "ip": ip,
                "name": msg.decode(FORMAT)
            })

        receiver_socket.close()

    return available_receivers


def get_receiver(available_receivers):
    """
    Get ip
    """
    for i, receiver in enumerate(available_receivers):
        print(f'{i+1}. {receiver.get("ip")} - {receiver.get("name")}')

    while True:
        res = input("\nChoose the receiver: ")

        if res.isdigit() and int(res) >= 1 and int(res) <= len(available_receivers):
            return available_receivers[int(res) - 1]
        else:
            print("Invalid input")


def send_file(conn, path):
    """
    Send file
    """
    filename = re.match(r'.*[\\/](?P<filename>.*)', path).groupdict()
    send_msg = f'{MSG_TYPES.get("filename"):<{MSG_HEADERS.get("type")}}' + \
        f'{len(filename):<{MSG_HEADERS.get("length")}}' + \
               filename.get("filename")
    conn.send(bytes(send_msg, FORMAT))

    time.sleep(1)

    file_content = open(path, "rb").read()
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

    conn.send(bytes(send_msg, FORMAT))


def start():
    ip = get_ip()
    network_ips = get_network_ips(ip)
    available_receivers = get_available_receivers(network_ips)

    print(f"{len(available_receivers)} available receiver" +
          ("" if len(available_receivers) == 1 else "s"))
    receiver = get_receiver(available_receivers)

    path = input("Insert the path of the file you want to send: ")
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver_socket.connect((receiver.get("ip"), PORT))
    send_file(conn=receiver_socket, path=path)


if __name__ == "__main__":
    start()
