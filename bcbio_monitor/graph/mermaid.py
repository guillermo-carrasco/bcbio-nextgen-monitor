"""Wrapper for mermaid JavaScript graph library http://knsv.github.io/mermaid/#mermaid"""

class GraphNode(object):
    """Represent the node of a Mermaid graph.

    Nodes can be squares, circles, asymetric shapes or rhombus.
    """
    def __init__(self, shape):
        """Initializes the node.

        :params shape: str: The shape of the node.
        """
        self.shapes {
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


class MermainGraph(object):
    """Data structure to represent a Mermaid graph"""
    def __init__(self):
        self.nodes = []
