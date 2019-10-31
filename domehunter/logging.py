import os
import logbook
from logbook import TimedRotatingFileHandler as TRFH
from logbook import StderrHandler as StdH


def set_up_logger(name,
                  logfilename,
                  log_file_level='NOTICE',
                  log_stderr_level='NOTICE',
                  logo=False):
    """Set up a logger with a log to file handler and log to stderr handler.

    Parameters
    ----------
    name : str
        The name of the logger, in most causes just use __name__.
    logfilename : str
        Filename for the log file of the logger instance.
    log_file_level : str
        Desired log file log level, check
        logbook.base._reverse_level_names.keys() for possible levels.
    log_stderr_level : type
        Desired stderr log level, check
        logbook.base._reverse_level_names.keys() for
        possible levels.
    logo : bool
        Toggle printing a huntsman logo in stderr upon initialising the logger.

    Returns
    -------
    logbook.Logger
        Returns the logger object.

    """
    logger = logbook.Logger(name)
    if logo:
        fmt_str = '{record.message:^120}'
        logger.handlers.append(logbook.StderrHandler(level='WARNING',
                                                     format_string=fmt_str))
        logofile = os.path.join(os.path.dirname(__file__), 'logo.txt')
        with open(logofile, 'r') as f:
                for line in f:
                    logger.warn(line.strip('\n'))
        logger.handlers = []

    fmt_str = ('[{record.time:%Y-%m-%d %H:%M:%S}][{record.level_name:*^11}] :'
               ' {record.message:~^45}'
               ' line {record.lineno:<3} in '
               '{record.module:<}.{record.func_name:<} ')

    logfilename = os.path.join(os.path.dirname(__file__), 'logs/', logfilename)
    logger.handlers.append(TRFH(logfilename,
                                level=log_file_level,
                                mode='a+',
                                date_format='%Y-%m-%d',
                                bubble=True,
                                format_string=fmt_str))

    logger.handlers.append(StdH(level=log_stderr_level,
                                bubble=True,
                                format_string=fmt_str))
    return logger


log_logger = set_up_logger(__name__, 'logging_log.log')


def get_log_level(level):
    """Returns the logbook log level corresponding to the supplied string.

    Parameters
    ----------
    level : str
        The name of the desired logging level.

    Returns
    -------
    new_level : int
        An integer corresponding to the requested log level.

    """
    levels = logbook.base._reverse_level_names
    try:
        new_level = levels[level]
    except KeyError:
        log_logger.error((f'Requested level [\'{level}\'] is not valid.'
                          f' Valid levels are {list(levels.keys())}.'))
        return
    return new_level


def get_handler(logger, handler):
    """Returns a specific handler from the logger so that log level can
    be adjusted if required.

    Parameters
    ----------
    logger : logbook.Logger object
        The Logger containing the handler we want to update.
    handler : str
        The desired handler from the logger.

    Returns
    -------
    handler : logbook.handler object
        The requested handler.

    """
    handlers = {'TRFH': TRFH,
                'StdH': StdH}
    try:
        requested_handler = handlers[handler]
    except KeyError:
        logger.error((f'Desired Handler [\'{requested_handler}\'] is not'
                      f' a valid handler type.'
                      f' Valid types are {list(levels.keys())}.'))
        return
    for handler in logger.handlers:
        if isinstance(handler, requested_handler):
            return handler


def update_handler_level(logger, handler, level):
    """Updates a handlers logging level.

    Parameters
    ----------
    logger : logbook.Logger object
        The Logger containing the handler we want to update.
    handler_type : str
        The name of the handler you want to update.
    level : str
        The name of the desired logging level.

    """
    new_level = get_log_level(level)
    handler_to_update = get_handler(logger, handler)
    if new_level is None or handler_to_update is None:
        log_logger.debug(f'Update logger handler level failed.')
        return
    handler_to_update.level = new_level
