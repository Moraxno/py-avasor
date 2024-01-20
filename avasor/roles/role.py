import datetime
import logging
from typing import Callable

class ClosedConnectionException(Exception):
    pass

class ShutdownServerException(Exception):
    pass

class Role:
    def __init__(self):
        self.logger = logging.getLogger(__file__)
        self.start_time = datetime.datetime.now()
        self._commands = {
            "close": self._close,
            "shutdown": self._shutdown
        }
    
    def _close(self):
        raise ClosedConnectionException
    
    def _shutdown(self):
        raise ShutdownServerException
    
    def register_command(self, msg: str, method: Callable):
        self._commands[msg] = method
    
    def handle_message(self, msg: str):
        method = self._commands.get(msg, None)
        
        if method:
            return method()
        else:
            return None
        