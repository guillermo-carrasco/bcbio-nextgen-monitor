import argparse
import os
import webbrowser

import bcbio_monitor.api

from flask import Flask
from gevent.wsgi import WSGIServer


from bcbio_monitor import graph, config, app
from bcbio_monitor import log

def cli():
    parser = argparse.ArgumentParser(description='Show bcbio-nextgen analysis status on a web browser')
    parser.add_argument('logfile', type=str, help="Path to the file bcbio-nextgen-debug.log")
    parser.add_argument('--config', type=str, default=os.path.join(os.environ.get('HOME'), '.bcbio/monitor.yaml'), \
        help="PAth to the configuration file, defaults to ~/.bcbio/monitor.yaml")
    parser.add_argument('--title', type=str, default='bcbio-nextgen analysis monitor', help=("Title (or name) for the analysis, "
                                                                                             "i.e NA12878 test"))
    parser.add_argument('--no-update', action='store_const', const='no_update', help="Don't update frontend " \
                                                                "with the last log line read (less requests)")
    parser.add_argument('--no-browser', action='store_const', const='no_browser', help="Don't open a new browser tab")
    parser.add_argument('--local', action='store_const', const='local', help=("Force the monitor to look for the log file locally "
                                                                              "(regardless of the configuration file.)"))
    args = parser.parse_args()

    custom_config = config.parse_config(args.config)

    # Initialize logging
    level = custom_config.get('log', {}).get('level')
    if level:
        try:
            log.set_level(level)
        except TypeError:
            raise RuntimeError(("The provided log level \"{}\" is not a valid option, please specify one "
                                "of the following levels: INFO, WARN, ERROR or DEBUG".format(level)))

    # If logfile is local, check that it exists
    if not custom_config.get('remote') or args.local:
        try:
            del(custom_config['remote'])
        except KeyError:
            pass
        if not os.path.exists(args.logfile):
            raise RuntimeError("Provided logfile does not exist or its not readable")

    # Modify app config with values from config file
    update = False if args.no_update else True
    app.config.update(logfile=args.logfile, title=args.title, update=update, **custom_config.get('server', {}))
    app.custom_configs = custom_config

    # Start application server
    host, port = app.config.get('SERVER_NAME').split(':')
    app.graph = graph.BcbioFlowChart(args.logfile, host, port, update, custom_config.get('remote', None))
    server = WSGIServer((host, int(port)), app)
    if not args.no_browser:
        webbrowser.open('http://{}'.format(app.config.get('SERVER_NAME')))
    server.serve_forever()
