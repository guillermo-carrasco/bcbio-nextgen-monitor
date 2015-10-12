"""Misc. utilities for bcbio-nextgen monitor"""

import time

def follow(_file):
    """Follows a file for continuous reading, like `tail -f` would do

    :params _file: str: Path to the file to follow
    """
    with open(_file, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line
