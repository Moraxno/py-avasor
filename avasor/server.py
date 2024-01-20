import argparse
import multiprocessing
from multiprocessing.connection import Listener, Connection
import os
import threading
import logging
from avasor.base import prepare_logging
from avasor.roles.borg_role import BorgRole

from avasor.roles.role import ClosedConnectionException, ShutdownServerException

import signal
import sys

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

def handle_connection(connection: "Connection"):
    logger.info("Connection accepted. New thread is now handling.")
    s = StatusRole()
    b = BorgRole()
    
    while not connection.closed:
        msg = connection.recv()
        
        try:
            # TODO: Make this iterate all roles
            result = s.handle_message(msg)
            if result:
                connection.send(result)
            else:
                result = b.handle_message(msg)
                connection.send(result)
        except ClosedConnectionException:
            connection.close()
            break
        except ShutdownServerException:
            connection.close()
            os.kill(os.getppid(), signal.SIGTERM)
            break
        except:
            connection.send(None)
    
    logger.info("Connection closed. Shutting down thread.")

def handle_listener(listener: "Listener"):
    global logger
    
    logger.info("Listener Thread is running.")
    
    while True:
        conn = listener.accept()
        logger.info("Connection accepted")
        connection_thread = threading.Thread(target=handle_connection, args=(conn, ), daemon=True)
        connection_thread.start()

def main():
    global logger
    
    signal.signal(signal.SIGINT, signal_handler)
    try:
        signal.signal(signal.SIGBREAK, signal_handler)
    except:
        pass
    
    args = parse_command_line()
    prepare_logging(args)
    
    logger = logging.getLogger(__file__)
    
    listener = Listener((args.address, args.port), authkey=args.authkey)
    
    listener_thread = threading.Thread(target=handle_listener, args=(listener, ), daemon=True)
    listener_thread.start()
    
    while True:
        pass
        


if __name__ == "__main__":
    main()