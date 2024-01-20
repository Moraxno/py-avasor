from dataclasses import dataclass
import datetime
import json
from avatar.roles.role import Role
import subprocess

BORG_REPO = "/media/FileBackup/borg-repo/"
BORG_COMMAND = "borg"

class GigaBytes(float):
    pass

    @staticmethod
    def from_bytes(bytes: int):
        return GigaBytes(bytes / 1024**3)

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

class BorgRole(Role):
    def __init__(self):
        super().__init__()
        
        self.register_command("info", self._run_info)
        
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

    @staticmethod
    def extract_last_modified_time(proc_result):
        return datetime.datetime.strptime(proc_result["repository"]["last_modified"], "%Y-%m-%dT%H:%M:%S.%f")
        
    @staticmethod
    def extract_uncompressed_size(proc_result):
        return GigaBytes.from_bytes(proc_result["cache"]["stats"]["total_size"])
    
    @staticmethod
    def extract_compressed_size(proc_result):
        return GigaBytes.from_bytes(proc_result["cache"]["stats"]["total_csize"])
    
    @staticmethod
    def extract_deduped_size(proc_result):
        return GigaBytes.from_bytes(proc_result["cache"]["stats"]["unique_csize"])
        
        
    
    