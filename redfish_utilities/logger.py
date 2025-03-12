import logging
import datetime
import redfish
import os


def get_debug_level(level):
    if level == "DEBUG":
        return logging.DEBUG
    elif level == "INFO":
        return logging.INFO
    elif level == "WARNING":
        return logging.WARNING
    elif level == "ERROR":
        return logging.ERROR
    elif level == "CRITICAL":
        return logging.CRITICAL
    else:
        raise ValueError(f"Invalid debug level: {level}")


def setup_logger(
    file_log: bool = False, stream_log: bool = True, log_level: str = "INFO", file_name: str = "redfish_utils"
):
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_level = get_debug_level(log_level)
    logger = logging.getLogger(__name__)

    if file_log:
        file_name = os.path.basename(file_name)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        log_file = f"{file_name}-{timestamp}.log".format()
        logger = redfish.redfish_logger(log_file, log_format, log_level)

    if stream_log:
        formatter = logging.Formatter(log_format)
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)
        logger.setLevel(log_level)

    return logger
