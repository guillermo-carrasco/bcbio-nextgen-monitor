"""Module to generate and work with process flowcharts"""

from graphviz import Digraph


class BcbioFlowChart(Digraph):
    """Representation for a graphviz bcbio-nextgen flowchart"""

    def __init__(self, name='bcbio-nextgen-flowchart', data=None):
        super(BcbioFlowChart, self).__init__(comment='bcbio flow chart', format='png', encoding='UTF8')
        self.name = name
        self._nodes = []
        if data:
            # Not doing anything with the timestamps by the moment
            for timestamp, step in data.iteritems():
                node_id = '_'.join(step.lower().split())
                self.node(node_id, step)
                self._nodes.append(node_id)
            if len(self._nodes) > 1:
                for i in range(1, len(self._nodes)):
                    self.edge(self._nodes[i-1], self._nodes[i])
