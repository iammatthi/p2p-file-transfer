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
    ips = socket.gethostbyname_ex(socket.gethostname())[2]
    if len(ips) > 1:
        print("Select your ip")
        for i, ip in enumerate(ips):
            print(f"{i+1}. {ip}")

        while True:
            res = input("\nChoose one option: ")

            if res.isdigit() and int(res) >= 1 and int(res) <= len(ips):
                return ips[int(res) - 1]
            else:
                print("Invalid input")
    else:
        return ips[0]
