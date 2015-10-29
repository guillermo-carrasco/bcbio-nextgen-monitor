"""Module to generate and work with process flowcharts"""

from graphviz import Digraph


class BcbioFlowChart(Digraph):
    """Representation for a graphviz bcbio-nextgen flowchart"""

    def __init__(self, name='bcbio-nextgen-flowchart', data=None):
        super(BcbioFlowChart, self).__init__(comment='bcbio flow chart', format='png', encoding='UTF8')
        self.name = name
        if data:
            # Not doing anything with the timestamps by the moment
            for step, timestamp in data.iteritems():
                self.node('_'.join(step.lower().split()), step)
