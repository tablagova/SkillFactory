def is_warning(record):
    return True if record.levelname == 'WARNING' else False


def is_debug(record):
    return True if record.levelname == 'DEBUG' or record.levelname == 'INFO' else False