import re
import socket
import sys
import time

from tqdm import tqdm

from src.peer import Peer
from src.utils import clear, get_ip


class Sender(Peer):

    def __init__(self):
        super().__init__()

    def start(self):
        clear()

        receiver = None

        print("1. Insert receiver ip")
        print("2. Scan the network")

        while True:
            res = input("\nChoose one option: ")

            if res == "1":
                receiver_ip = input("Insert the receiver's ip: ")
                receiver = {
                    "ip": receiver_ip,
                    "name": "Unknown"
                }
                break

            elif res == "2":
                clear()
                ip = get_ip()
                clear()
                network_ips = self.get_network_ips(ip)
                clear()
                available_receivers = self.get_available_receivers(network_ips)
                clear()
                receiver = self.get_receiver(available_receivers)
                break

            else:
                print("Invalid input")

        clear()

        receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        receiver_socket.connect((receiver.get("ip"), self.port))
        self.send(conn=receiver_socket, msg_type=self.msg_types.get(
            "register"), msg=self.name)
        try:
            while True:
                path = input("Insert the path of the file you want to send: ")

                filename = re.match(
                    r'.*[\\/](?P<filename>.*)', path).groupdict().get("filename")
                self.send(conn=receiver_socket, msg_type=self.msg_types.get(
                    "filename"), msg=filename)
                print(
                    f'Waiting for {receiver.get("name")} ({receiver.get("ip")})\'s response')
                msg_type = self.receive_type(conn=receiver_socket)
                if msg_type == self.msg_types.get("response"):
                    msg_length = self.receive_length(conn=receiver_socket)
                    res = self.receive_msg(
                        conn=receiver_socket, msg_length=msg_length).decode(self.format)

                    if res == "n":
                        print(
                            f'{receiver.get("name")} ({receiver.get("ip")}) has refused the file')
                    else:
                        print("Sending the file..")
                        self.send_file(conn=receiver_socket, path=path)
        except KeyboardInterrupt:
            self.send(conn=receiver_socket,
                      msg_type=self.msg_types.get("disconnect"))

    def get_network_ips(self, ip):
        """
        Get network
        """
        print("Select your network")
        ip_networks = re.match(
            r'(?P<small>(?P<wide>\d{1,3}\.\d{1,3})\.\d{1,3})\.\d{1,3}', ip).groupdict()
        print(f"1. {ip_networks.get('wide')}.0.0 (not supported yet)")
        print(f"2. {ip_networks.get('small')}.0")

        while True:
            res = input("\nChoose one option: ")

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

    def get_available_receivers(self, network_ips):
        """
        Get available receivers
        """
        print("Scanning the network for receivers..")
        available_receivers = []
        for ip in tqdm(network_ips):
            receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(0.5)

            result = receiver_socket.connect_ex((ip, self.port))
            if result == 0:
                name = "Unknown"

                self.send(conn=receiver_socket,
                          msg_type=self.msg_types.get("name"))

                msg_type = self.receive_type(conn=receiver_socket)
                if msg_type == self.msg_types.get("response"):
                    msg_length = self.receive_length(conn=receiver_socket)
                    name = self.receive_msg(
                        conn=receiver_socket, msg_length=msg_length).decode(self.format)

                available_receivers.append({
                    "ip": ip,
                    "name": name
                })

            receiver_socket.close()

        return available_receivers

    def get_receiver(self, available_receivers):
        """
        Get ip
        """
        print("Select the receiver")
        for i, receiver in enumerate(available_receivers):
            print(f'{i+1}. {receiver.get("name")} ({receiver.get("ip")})')

        while True:
            res = input("\nChoose one option: ")

            if res.isdigit() and int(res) >= 1 and int(res) <= len(available_receivers):
                return available_receivers[int(res) - 1]
            else:
                print("Invalid input")
