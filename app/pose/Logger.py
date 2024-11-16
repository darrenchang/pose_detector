import logging


class Logger:
    def __init__(
        self,
        name: str = "default_logger_name",
        logging_level: int = logging.INFO,
    ) -> None:
        self.logging_level = logging.INFO
        formatter = logging.Formatter("[%(asctime)s] %(name)s:%(lineno)s - %(levelname)s: %(message)s")
        self.logger = logging.getLogger(name)
        self.propagte = False
        self.logger.setLevel(logging_level)
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def get_logger(self):
        return self.logger
