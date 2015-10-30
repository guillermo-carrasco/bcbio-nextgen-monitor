"""Module to generate and work with process flowcharts"""
import threading
import time

from collections import OrderedDict

from graphviz import Digraph
from bcbio_monitor import parser as ps

class BcbioFlowChart(Digraph):
    """Representation for a graphviz bcbio-nextgen flowchart"""

    def __init__(self, logfile, name='bcbio-nextgen-flowchart'):
        super(BcbioFlowChart, self).__init__(comment='bcbio flow chart', format='png', encoding='UTF8')
        self.name = name
        self.logfile = logfile
        self._nodes = []
        self._times = OrderedDict()
        data = ps.get_bcbio_timings(logfile)
        self._reading_thread = threading.Thread(target=self.follow_log)
        # Daemonise the thread so that it's killed with Ctrl+C
        self._reading_thread.daemon = True
        self._reading_thread.start()
        # ALL THIS CODE SHOULD MOVE TO ANOTHER MERYOD THAT SHOULD WORK ATOMICALLY ON LOG LINES
        # if data:
        #     # Not doing anything with the timestamps by the moment
        #     for timestamp, step in data.iteritems():
        #         node_id = '_'.join(step.lower().split())
        #         self.node(node_id, step)
        #         self._nodes.append(node_id)
        #         self._times[node_id] = {"timestamp": timestamp}
        #     if len(self._nodes) > 1:
        #         for i in range(1, len(self._nodes)):
        #             self.edge(self._nodes[i-1], self._nodes[i])
        #             self._times[self._nodes[i-1]]['status'] = "finished"
        #
        #     self._times[self._nodes[-1]]['status'] = "finished" if self._nodes[-1] == "finished" else "running"

    def follow_log(self):
        """Reads a logfile continuously and updates internal graph if new step is found"""
        with open(self.logfile, 'r') as f:
            analysis_finished = False
            while not analysis_finished:
                line = f.readline()
                if not line:
                    time.sleep(1)
                    continue
                parsed_line = ps.parse_log_line(line)
                analysis_finished = (parsed_line['step'] == 'finished')

                # If this is a new step, update internal data
                if parsed_line['step']:
                    node_id = '_'.join(parsed_line['step'].lower().split())
                    self.node(node_id, parsed_line['step'])
                    self._nodes.append(node_id)
                    n_nodes = len(self._nodes)
                    if n_nodes > 1:
                        self.edge(self._nodes[n_nodes - 2], self._nodes[n_nodes -1])

                # In any case, update the flowchart frontend with the new line
                self.update_flowchart(ps.parse_log_line(line))

    def get_times(self):
        return self._times

    def update_flowchart(self, info):
        """Updates frontend with info from the log

        :param info: dict - Information from a line in the log. i.e regular line, new step.
        """
        pass
