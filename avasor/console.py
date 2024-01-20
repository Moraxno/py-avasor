import argparse
import multiprocessing
from multiprocessing.connection import Client
import threading
import logging

import signal
import sys
from avasor.base import prepare_logging

logger = None

from roles.status_role import StatusRole

def signal_handler(sig, frame):
    global logger
    logger.warning("Shutdown per user request.")
    sys.exit(0)

def parse_command_line():
    ap = argparse.ArgumentParser("avasor Server")
    ap.add_argument("--address", default="localhost")
    ap.add_argument("--port", "-p", default=64123, type=int)
    ap.add_argument("--authkey", "-k", default=b"secret", type=bytes)
    ap.add_argument("--verbose", "-v", action="count", default=0)
    ap.add_argument("--quiet", "-q", action="count", default=0)
    
    return ap.parse_args()


def main():
    global logger
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGBREAK, signal_handler)
    
    args = parse_command_line()
    prepare_logging(args)
    logger = logging.getLogger(__file__)
    
    logger.info("logger ready")
    
    
    while True:
        try:
            client = Client((args.address, args.port), authkey=args.authkey)
        except ConnectionRefusedError:
            logger.warning("Server is not responding, trying again.")
            continue
        except ConnectionResetError:
            logger.warning("Server denies the communication.")
            continue
            
        logger.info("Client ready")
    
        while not client.closed:
            msg = input("$ ")
            try:
                client.send(msg)
                answer = client.recv()
            except EOFError:
                logger.warning("Communication ended.")
                client.close()
                break
            except ConnectionResetError:
                logger.warning("Server ended the communication.")
                break
                
            print(f"> {answer}")



if __name__ == "__main__":
    main()