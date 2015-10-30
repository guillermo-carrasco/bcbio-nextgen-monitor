import argparse
import os
import time

import gevent

from flask import Flask, Response, request, render_template, send_from_directory, jsonify
from gevent.wsgi import WSGIServer
from gevent.queue import Queue

from bcbio_monitor import graph, config
from bcbio_monitor import parser as ps

# App initialization
app = Flask(__name__, static_url_path='/static')
subscriptions = []

###############
# controllers #
###############
# SSE "protocol" is described here: http://mzl.la/UPFyxY
class ServerSentEvent(object):

    def __init__(self, data):
        self.data = data
        self.event = None
        self.id = None
        self.desc_map = {
            self.data : "data",
            self.event : "event",
            self.id : "id"
        }

    def encode(self):
        if not self.data:
            return ""
        lines = ["%s: %s" % (v, k)
                 for k, v in self.desc_map.iteritems() if k]

        return "%s\n\n" % "\n".join(lines)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')


@app.route('/js/<path:path>')
def static_proxy(path):
    mime = 'application/javascript'
    return Response(app.send_static_file(os.path.join('js', path)), mime)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/")
def index():
    return render_template('index.html', **app.config)


@app.route("/publish", methods=['POST'])
def publish():
    for sub in subscriptions[:]:
        sub.put(request.data)
    gevent.spawn(notify)

    return "OK"


@app.route("/subscribe")
def subscribe():
    def gen():
        q = Queue()
        subscriptions.append(q)
        try:
            while True:
                result = q.get()
                ev = ServerSentEvent(str(result))
                yield ev.encode()
        except GeneratorExit: # Or maybe use flask signals
            subscriptions.remove(q)

    return Response(gen(), mimetype="text/event-stream")


###################
#       API       #
###################
@app.route('/api/graph', methods=['GET'])
def get_graph():
    """Creates a new graph or updates an existing one with a new node"""
    # Table data needs to be an array of dicts to keep sorted when sent to JS
    _table_data = [{s: st} for s, st in app.graph.get_times().items()]
    return jsonify(graph_data=app.graph.source, table_data=_table_data)


###################
#      Main       #
###################
def main():
    parser = argparse.ArgumentParser(description='Plot bcbio-nextgen analysis status on a small webb application')
    parser.add_argument('logfile', type=str, help="Path to the file bcbio-nextgen-debug.log")
    parser.add_argument('--config', type=str, default=os.path.join(os.environ.get('HOME'), '.bcbio/monitor.yaml'), \
        help="PAth to the configuration file, defaults to ~/.bcbio/monitor.yaml")
    parser.add_argument('--title', type=str, default='bcbio-nextgen analysis monitor', help=("Title (or name) for the analysis, "
                                                                                             "i.e NA12878 test"))
    args = parser.parse_args()
    if not os.path.exists(args.logfile):
        raise RuntimeError('Provided log file {} does not exist or is not readable.'.format(args.logfile))
    _config = config.parse_config(args.config)
    app.config.update(logfile=args.logfile, title=args.title, **_config.get('flask', {}))
    app.custom_configs = _config
    app.graph = graph.BcbioFlowChart(args.logfile)
    host, port = app.config.get('SERVER_NAME').split(':')
    server = WSGIServer((host, int(port)), app)
    server.serve_forever()
