import logging


def create_logger(logger_name, log_file_path=None):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    file_handler = None
    if log_file_path is not None:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    if file_handler is not None:
        file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    if file_handler is not None:
        logger.addHandler(file_handler)

    return logger


LOGGER = create_logger("core")
