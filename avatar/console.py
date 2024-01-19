import argparse
import multiprocessing
from multiprocessing.connection import Client
import threading
import logging

import signal
import sys

logger = None

from roles.status_role import StatusRole

def signal_handler(sig, frame):
    global logger
    logger.warning("Shutdown per user request.")
    sys.exit(0)

def parse_command_line():
    ap = argparse.ArgumentParser("Avatar Server")
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
    logger = prepare_logger(args)
    
    logger.info("logger ready")
    
    client = Client((args.address, args.port), authkey=args.authkey)
    
    logger.info("Client ready")
    
    while not client.closed:
        msg = input("$ ")
        try:
            client.send(msg)
            answer = client.recv()
        except EOFError:
            print("! The server has ended the communication.")
            client.close()
            break
            
        print(f"> {answer}")
        

def prepare_logger(args):
    base_level = logging.WARNING
    offset = (args.quiet - args.verbose) * 10
    log_level = base_level + offset
    log_level = max(logging.DEBUG, min(logging.CRITICAL, log_level))
    
    logging.basicConfig(
        level=log_level,
        format="[%(levelname)8s] %(message)s"
    )
    
    logger = logging.getLogger(__file__)
    return logger
    


if __name__ == "__main__":
    main()