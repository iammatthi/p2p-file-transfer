import logging
import logging.config
import re
import socket

from abc import ABC, abstractmethod

from src.config import get_config, get_logger_config
from src.utils import clear


class Peer(ABC):

    def __init__(self):
        logging.config.dictConfig(get_logger_config())
        self.logger = logging.getLogger(__name__)

        self.msg_headers = get_config("msg", "headers")
        self.msg_types = get_config("msg", "types")
        self.port = get_config("port")
        self.format = get_config("format")

        self.name = input("Insert your name: ")

    def log(self, message):
        self.logger.info(message)

    def send(self, conn, msg_type, msg=None):
        """
        Send message
        """
        send_msg = f'{msg_type:<{self.msg_headers.get("type")}}'

        if msg:
            send_msg += f'{len(msg):<{self.msg_headers.get("length")}}' + msg

        conn.sendall(bytes(send_msg, self.format))

    def send_file(self, conn, path):
        """
        Send file
        """
        file_content = open(path, "rb").read()
        send_msg = f'{self.msg_types.get("file"):<{self.msg_headers.get("type")}}' + \
            f'{len(file_content):<{self.msg_headers.get("length")}}'
        conn.sendall(bytes(send_msg, self.format) + file_content)

    def receive_type(self, conn):
        msg_type = conn.recv(self.msg_headers.get("type")).decode(self.format)
        if not msg_type:
            return False

        return msg_type.strip()

    def receive_length(self, conn):
        msg_length = conn.recv(self.msg_headers.get(
            "length")).decode(self.format)
        if not msg_length:
            return False

        return int(msg_length.strip())

    def receive_msg(self, conn, msg_length):
        msg_bytes = b''
        remining_msg_length = msg_length

        while remining_msg_length > 0:
            min_length = min(remining_msg_length, 4096)

            downloaded_bytes_length = conn.recv(min_length)
            msg_bytes += downloaded_bytes_length
            remining_msg_length -= len(downloaded_bytes_length)

        return msg_bytes

    @abstractmethod
    def start(self):
        pass
