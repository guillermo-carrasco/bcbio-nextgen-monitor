"""Module to generate and work with process flowcharts"""

from collections import OrderedDict

from graphviz import Digraph
from bcbio_monitor import parser as ps

class BcbioFlowChart(Digraph):
    """Representation for a graphviz bcbio-nextgen flowchart"""

    def __init__(self, logfile, name='bcbio-nextgen-flowchart'):
        super(BcbioFlowChart, self).__init__(comment='bcbio flow chart', format='png', encoding='UTF8')
        self.name = name
        self._nodes = []
        self._times = OrderedDict()
        data = ps.get_bcbio_timings(logfile)
        if data:
            # Not doing anything with the timestamps by the moment
            for timestamp, step in data.iteritems():
                node_id = '_'.join(step.lower().split())
                self.node(node_id, step)
                self._nodes.append(node_id)
                self._times[node_id] = {"timestamp": timestamp}
            if len(self._nodes) > 1:
                for i in range(1, len(self._nodes)):
                    self.edge(self._nodes[i-1], self._nodes[i])
                    self._times[self._nodes[i-1]]['status'] = "finished"

            self._times[self._nodes[-1]]['status'] = "finished" if self._nodes[-1] == "finished" else "running"

    def get_times(self):
        return self._times
