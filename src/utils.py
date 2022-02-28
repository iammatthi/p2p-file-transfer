import socket

from os import system, name


def clear():
    if name == 'nt':
        # for windows
        _ = system('cls')
    else:
        # for mac and linux(here, os.name is 'posix')
        _ = system('clear')


def get_ip():
    """
    Get ip
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]
