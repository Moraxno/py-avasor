import datetime
import logging
import psutil

from avasor.roles.role import Role



class StatusRole(Role):
    def __init__(self):
        super().__init__()
        
        self.register_command("cpu", self._run_cpu)
        self.register_command("memory", self._get_memory)
        self.register_command("ping", self._run_ping)
        self.register_command("uptime", self._run_uptime)
    
    def _run_cpu(self):
        return psutil.cpu_percent()
    
    def _get_memory(self):
        memory = psutil.virtual_memory()
        used, total = memory.used, memory.total
        
        self.logger.debug("Used memory %.2f GB", used / 1024**3)
        self.logger.debug("Total memory %.2f GB", total / 1024**3)
        
        return (used, total)
    
    def _run_ping(self):
        return "pong"
        
    def _run_uptime(self):
        return datetime.datetime.now() - self.start_time
    