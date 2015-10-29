"""Wrapper for mermaid JavaScript graph library http://knsv.github.io/mermaid/#mermaid"""

from datetime import datetime

class GraphNode(object):
    """Represent the node of a Mermaid graph.

    Nodes can be squares, circles, asymetric shapes or rhombus.
    """
    def __init__(self, name, shape, orientation='TD'):
        """Initializes the node.

        :param name: str - Name of the node
        :param shape: str: The shape of the node.
        :param orientation: str - Orientation of the graph; Top-Down (TD), Left-Right (LR), etc.
        """
        # If orientation is defined, then this is a header node and doesn't need a shape
        self.name = name
        self.shape = None
        if name == 'graph':
            self.orientation = orientation
            self.header = True
        else:
            self.shapes = {
                'circle': {
                    'open': '(',
                    'close': ')'
                },
                'asymetric': {
                    'open': '>',
                    'close': ']'
                },
                'square': {
                    'open': '[',
                    'close': ']'
                },
                'rhombus': {
                    'open': '{',
                    'close': '}'
                }
            }
            try:
                self.shape = shapes[shape]
            except KeyError as e:
                raise e("The specified shape is not valid. Please use one of these shapes: {}".format(' '.join(shapes.keys())))


    def __str__(self):
        if self.shape:
            return ''
        else:
            return "{} {};\n".format(self.name, self.orientation)



class MermainGraph(object):
    """Data structure to represent a Mermaid graph"""
    def __init__(self, data=None, orientation='TD'):
        """Represents a Mermaid graph.

        :param data: dict - Initialize the graph with data.
        :param orientation: str - Define orientation of the graph: TD, BT, LR, RL
        """
        self.nodes = []
        self.callbacks = []
        orientations = ['TD', 'BT', 'LR', 'LR']
        assert orientation in orientations, "Orientation is not any of {}".format(' '.join(orientations))
        header_node = GraphNode('graph', None, orientation)
        self.nodes.append(header_node)

        if data:
            assert all([type(d) == datetime and type(s) == str for d, s in data.items()]), \
                "Data format for the graph seems to be wrong, please use a dictionary like \{datetime.datetime: string\}"


    def __str__(self):
        """Return a string representation of the graph"""
        return ''.join([str(node) for node in self.nodes])


    def get_graph_data(self, as_string=False):
        """Return graph data

        :param as_string: str - Returns a formated string representing graph data
        """
        if as_string:
            return ''.join([str(node) for node in self.nodes])
        else:
            return self.nodes


    def set_callback(self, callback_method, hover_text):
        """Attaches a callback method to a node"""
        raise NotImplementedError()
