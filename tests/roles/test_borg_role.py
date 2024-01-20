import datetime
import json

import pytest
from avatar.roles.borg_role import BorgRole


@pytest.fixture()
def borg_info_object():
    with open("tests/__assets__/borg.info.txt") as f:
        cmd_output = f.read()
    cmd_result = json.loads(cmd_output)
    yield cmd_result

def test_extract_last_modified(borg_info_object):  
    extracted = BorgRole.extract_last_modified_time(borg_info_object)
    
    assert extracted == datetime.datetime(2024, 1, 20, 16, 00, 51, 0)
    
def test_extract_uncompressed_size(borg_info_object):
    extracted = BorgRole.extract_uncompressed_size(borg_info_object)
    
    assert extracted == 399677665438 / (1024**3)
    
def test_extract_compressed_size(borg_info_object):
    extracted = BorgRole.extract_compressed_size(borg_info_object)
    
    assert extracted == 257222411750 / (1024**3)
    
def test_extract_deduped_size(borg_info_object):
    extracted = BorgRole.extract_deduped_size(borg_info_object)
    
    assert extracted == 39095180520 / (1024**3)
    