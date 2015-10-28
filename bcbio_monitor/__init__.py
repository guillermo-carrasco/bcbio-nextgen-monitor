import argparse
import os

from flask import Flask, render_template, send_from_directory
from bcbio_monitor import parser

# App initialization
app = Flask(__name__, static_url_path='/static')
app.config.update(
    DEBUG = True,
)

###############
# controllers #
###############
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
    timings = parser.get_bcbio_timings(app.config.get('logfile'))
    import ipdb; ipdb.set_trace()
    return render_template('index.html')

def main():
    parser = argparse.ArgumentParser(description='Plot bcbio-nextgen analysis status on a small webb application')
    parser.add_argument('logfile', type=str, help="Path to the file bcbio-nextgen-debug.log")
    args = parser.parse_args()
    if not os.path.exists(args.logfile):
        raise RuntimeError('Provided log file {} does not exist or is not readable.'.format(args.logfile))
    app.config.update(logfile=args.logfile)
    app.run()
