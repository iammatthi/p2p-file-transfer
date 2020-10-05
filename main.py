import sys
import os

from src import Receiver, Sender
from src.utils import clear


def main():
    clear()
    
    print("Select your rule")
    print(f'1. Receiver')
    print(f'2. Sender')

    while True:
        res = input("\nChoose one option: ")

        if res == "1":
            peer = Receiver()
            peer.start()
            break
        elif res == "2":
            peer = Sender()
            peer.start()
            break
        else:
            print("Invalid input")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    # except Exception as e:
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #     print(e, exc_type, fname, exc_tb.tb_lineno)
