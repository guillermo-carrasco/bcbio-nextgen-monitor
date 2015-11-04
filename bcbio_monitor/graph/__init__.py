"""Module to generate and work with process flowcharts"""
import json
import threading
import time

import requests

from collections import OrderedDict

from bcbio_monitor import parser as ps
from graphviz import Digraph
from paramiko import client

class BcbioFlowChart(Digraph):
    """Representation for a graphviz bcbio-nextgen flowchart"""

    def __init__(self, logfile, host='localhost', port='5000', update=True, remote=None):
        """Initialices a BcbioFlowChart object.

        :param logfile: str - Path to the logfile where to extract information
        :param host: str - Host address where the monitor is running
        :param port: str - Port where the monitor is listening
        :param update: boolean - Update frontend on every line read
        :param remote: dict - Connection parameters if the log is on a remote host.
        """
        super(BcbioFlowChart, self).__init__(comment='bcbio flow chart', format='png', encoding='UTF8')
        self.logfile = logfile
        self.update = update
        self.remote = remote
        self.base_url = "http://{}".format(':'.join([host, port]))
        self._nodes = []
        self._steps = []
        self._reading_thread = threading.Thread(target=self.follow_log)
        # Daemonise the thread so that it's killed with Ctrl+C
        self._reading_thread.daemon = True
        self._reading_thread.start()


    def follow_log(self):
        """Reads a logfile continuously and updates internal graph if new step is found"""
        # Server needs to be up and running before starting sending POST requests
        time.sleep(5)
        try:
            if self.remote:
                cl = client.SSHClient()
                # Try to load system keys
                cl.load_system_host_keys()
                cl.connect(self.remote['host'], port=self.remote.get('port', 22), username=self.remote.get('username', None), \
                           password=self.remote.get('password', None))
                sftp = cl.open_sftp()
                f = sftp.open(self.logfile, 'r')
            else:
                f = open(self.logfile, 'r')
        except IOError:
            raise RuntimeError("Provided logfile does not exist or its not readable")
        analysis_finished = False
        last_line_read = False
        while not analysis_finished:
            line = f.readline()
            if not line:
                last_line_read = True
                time.sleep(1)
                continue
            parsed_line = ps.parse_log_line(line)
            analysis_finished = (parsed_line['step'] == 'finished') or (parsed_line['step'] == 'error')

            # If this is a new step, update internal data
            if parsed_line['step'] and not parsed_line['step'] == 'error':
                self._steps.append(parsed_line)
                node_id = '_'.join(parsed_line['step'].lower().split())
                self.node(node_id, parsed_line['step'])
                self._nodes.append(node_id)
                n_nodes = len(self._nodes)
                if n_nodes > 1:
                    self.edge(self._nodes[n_nodes - 2], self._nodes[n_nodes -1])

            # Update frontend only if its a new step _or_ the update flag is set to true and we are
            # not loading the log for the first time
            if (last_line_read and self.update) or parsed_line['step']:
                self.update_frontend(parsed_line)
        f.close()


    def update_frontend(self, info):
        """Updates frontend with info from the log

        :param info: dict - Information from a line in the log. i.e regular line, new step.
        """
        headers = {'Content-Type': 'text/event-stream'}
        if info.get('when'):
            info['when'] = info['when'].isoformat()
        requests.post(self.base_url + '/publish', data=json.dumps(info), headers=headers)


    def get_table_data(self):
        """Return information about registered steps"""
        return self._steps
