"""Methods and utilities to parse bcbio-nextgen log file.

Some methods have been re-used from the source code of bcbio-nextgen. The reason for not impotim then
and copying the code instead is that as a monitor tool, I don't want to force the installaion of bcbio-nextgen
on the user machine.
"""


def get_bcbio_timings(path):
    """Fetch timing information from a bcbio log file."""
    with open(path, 'r') as file_handle:
        steps = {}
        for line in file_handle:
            matches = re.search(r'^\[([^\]]+)\] ([^:]+: .*)', line)
            if not matches:
                continue

            tstamp = matches.group(1)
            msg = matches.group(2)

            if not msg.find('Timing: ') >= 0:
                continue

            when = datetime.strptime(tstamp, '%Y-%m-%dT%H:%MZ').replace(
                tzinfo=pytz.timezone('UTC'))
            step = msg.split(":")[-1].strip()
            steps[when] = step

        return steps
