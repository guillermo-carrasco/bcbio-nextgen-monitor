import argparse
import os
import time
import webbrowser

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
    data = request.data
    def notify():
        for sub in subscriptions[:]:
            sub.put(data)
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
def get_graph_data():
    """Returns Graphviz definition to build a graph in JS"""
    return jsonify(graph_data=app.graph.source)


@app.route('/api/progress_table', methods=['GET'])
def get_table_data():
    """Returns information about the registered steps"""
    return jsonify(table_data=app.graph.get_table_data())


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
    parser.add_argument('--no-update', action='store_const', const='no_update', help="Don't update frontend " \
                                                                "with the last log line read (less requests)")
    args = parser.parse_args()

    custom_config = config.parse_config(args.config)
    if not custom_config.get('remote') and not os.path.exists(args.logfile):
        raise RuntimeError("Provided logfile does not exist or its not readable")
    update = False if args.no_update else True
    app.config.update(logfile=args.logfile, title=args.title, update=update, **custom_config.get('flask', {}))
    app.custom_configs = custom_config
    host, port = app.config.get('SERVER_NAME').split(':')
    app.graph = graph.BcbioFlowChart(args.logfile, host, port, update, custom_config.get('remote', None))
    server = WSGIServer((host, int(port)), app)
    webbrowser.open('http://{}'.format(app.config.get('SERVER_NAME')))
    server.serve_forever()
