"""Definition of the API for bcbio-nextgen monitor"""
from bcbio_monitor import app

app.@route('/api/graph', methods=['POST'])
def update_graph(id, nodes=None):
    """Creates a new graph or updates an existing one with a new node"""
    pass
