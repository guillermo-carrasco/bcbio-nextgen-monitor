"""API calls for the Flask application"""

import os

import gevent

from flask import Response, request, render_template, send_from_directory, jsonify
from gevent.queue import Queue

from bcbio_monitor import app
from bcbio_monitor import parser as ps

#############################################
# controllers and static path configuration #
#############################################

# SSE "protocol" is described here: http://mzl.la/UPFyxY
subscriptions = []

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


###################
#       API       #
###################
@app.route('/runs_info', methods=['GET'])
def get_runs_info():
    """Return all runs info in a single API call"""
    return jsonify(data=app.analysis.get_runs_info())


@app.route('/graph_source', methods=['GET'])
def graph_source_for_run():
    run_id = request.args.get('run', 1)
    return jsonify(graph_source=app.analysis.graph_source_for_run(int(run_id) - 1))


@app.route('/steps', methods=['GET'])
def table_data_for_run():
    run_id = request.args.get('run', 0)
    return jsonify(steps=app.analysis.table_data_for_run(int(run_id) - 1))


@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(app.analysis.get_status())


@app.route('/last_message', methods=['GET'])
def get_last_message():
    """Returns last message read by the monitor"""
    return jsonify(app.analysis.get_last_message())


@app.route('/summary', methods=['GET'])
def summary():
    """Get summary of a finished analysis"""
    return jsonify(app.analysis.get_summary())
