"""Methods and utilities to parse bcbio-nextgen log file.

Some methods have been re-used from the source code of bcbio-nextgen. The reason for not impotim then
and copying the code instead is that as a monitor tool, I don't want to force the installaion of bcbio-nextgen
on the user machine.
"""
import pytz
import re

from datetime import datetime

def parse_log_line(line):
    """Parses a log line and returns it with more information

    :param line: str - A line from a bcbio-nextgen log
    :returns dict: A dictionary containing the line, if its a new step if its a Traceback or if the
                   analysis is finished
    """
    matches = re.search(r'^\[([^\]]+)\] ([^:]+: .*)', line)
    error = re.search(r'Traceback', line)
    if error:
        return {'line': line, 'step': 'error'}
    if not matches:
        return {'line': line, 'step': None}

    tstamp = matches.group(1)
    msg = matches.group(2)

    if not msg.find('Timing: ') >= 0:
        return {'line': line, 'step': None}

    when = datetime.strptime(tstamp, '%Y-%m-%dT%H:%MZ').replace(
        tzinfo=pytz.timezone('UTC'))
    step = msg.split(":")[-1].strip()
    return {'line': line, 'step': step, 'when': when}
