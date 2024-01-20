from dataclasses import dataclass
import datetime
import json
import os
from avasor.roles.role import Role
import subprocess
from enum import Enum

BORG_REPO = "/media/FileBackup/borg-repo/"
BORG_COMMAND = "borg"

class GigaBytes(float):
    pass

    @staticmethod
    def from_bytes(bytes: int):
        return GigaBytes(bytes / 1024**3)

def parse_borg_time(time_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f")

@dataclass
class BorgInfo:
    last_modified: datetime
    uncompressed_size: GigaBytes
    compressed_size: GigaBytes
    deduped_size: GigaBytes

@dataclass
class BorgArchive:
    name: str
    last_modified: datetime
    
ARCHIVES_OK_MESSAGE = b"Archive consistency check complete, no problems found."

class BorgRoleCommand(Enum):
    INFO = 0
    LIST = 1
    CONSISTENCY = 2
    
BRG = BorgRoleCommand
    
CMD_LOOKUP = {
    BorgRoleCommand.INFO: "info",
    BorgRoleCommand.LIST: "list",
    BorgRoleCommand.CONSISTENCY: "consistency",
}

class BorgRole(Role):
    def __init__(self):
        super().__init__()
        
        self.register_command(CMD_LOOKUP[BRG.INFO], self._run_info)
        self.register_command(CMD_LOOKUP[BRG.LIST], self._run_list)
        self.register_command(CMD_LOOKUP[BRG.CONSISTENCY], self._run_check)

    def _run_info(self):
        proc = subprocess.run([BORG_COMMAND, "info", "--json", BORG_REPO], stdout=subprocess.PIPE)
        proc.check_returncode()
        
        proc_result = json.loads(proc.stdout)
        
        edit_time = BorgRole.extract_last_modified_time(proc_result)
        uncompressed_size = BorgRole.extract_uncompressed_size(proc_result)
        compressed_size = BorgRole.extract_uncompressed_size(proc_result)
        deduped_size = BorgRole.extract_uncompressed_size(proc_result)
        
        borg_info = BorgInfo(
            edit_time,
            uncompressed_size,
            compressed_size,
            deduped_size
        )
        
        return borg_info
    
    def _run_list(self):
        proc = subprocess.run([BORG_COMMAND, "list", "--json", BORG_REPO], stdout=subprocess.PIPE)
        proc.check_returncode()
        
        proc_result = json.loads(proc.stdout)
        
        borg_archives = []
        
        for entry in proc_result["archives"]:
            name = entry["name"]
            time = parse_borg_time(entry["time"])
            
            borg_archive = BorgArchive(name, time)
            borg_archives.append(borg_archive)
        
        return borg_archives

    def _run_check(self):
        proc = subprocess.run([BORG_COMMAND, "check", "--archives-only", "-vv", BORG_REPO], stdout=subprocess.PIPE)
        proc.check_returncode()
        
        for line in proc.stdout.split(os.linesep):
            if line == ARCHIVES_OK_MESSAGE:
                return True
        
        return False

    @staticmethod
    def extract_last_modified_time(proc_result):
        return parse_borg_time(proc_result["repository"]["last_modified"])
        
    @staticmethod
    def extract_uncompressed_size(proc_result):
        return GigaBytes.from_bytes(proc_result["cache"]["stats"]["total_size"])
    
    @staticmethod
    def extract_compressed_size(proc_result):
        return GigaBytes.from_bytes(proc_result["cache"]["stats"]["total_csize"])
    
    @staticmethod
    def extract_deduped_size(proc_result):
        return GigaBytes.from_bytes(proc_result["cache"]["stats"]["unique_csize"])
        
        
    
    