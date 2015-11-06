import logging

# get root logger
ROOT_LOG = logging.getLogger()
ROOT_LOG.setLevel(logging.INFO)

# Console logger
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
ROOT_LOG.addHandler(stream_handler)

LOG_LEVELS = {
    'ERROR': logging.ERROR,
    'WARN': logging.WARN,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG
}

def set_level(level):
    ROOT_LOG.setLevel(level)

# XXX: Not used by now
def init_logger_file(log_file, log_level='INFO'):
    """ Append a FileHandler to the root logger.
    :param str log_file: Path to the log file
    :param str log_level: Logging level
    """
    log_level = LOG_LEVELS[log_level] if log_level in LOG_LEVELS.keys() else logging.INFO

    ROOT_LOG.setLevel(log_level)

    file_handle = logging.FileHandler(log_file)
    file_handle.setLevel(log_level)
    file_handle.setFormatter(formatter)
    ROOT_LOG.addHandler(file_handle)
