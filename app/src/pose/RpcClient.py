from time import sleep

import rpyc

from pose.Logger import Logger

logger = Logger(__name__).get_logger()


class RpcClient:
    def __init__(self, socket_path: str = None) -> None:
        self.conn = None
        self.socket_path = socket_path
        logger.info("RpcClient")
        self.config = {"sync_request_timeout": 180}

    def __connect(self, retry: int = 3) -> None:
        if retry <= 0:
            return None
        try:
            self.conn = rpyc.utils.factory.unix_connect(self.socket_path, config=self.config)
        except Exception as e:
            logger.debug(f"{__name__} failed to connect to server: {e}")
            logger.debug(f"{__name__} [Config used] socket:{self.socket_path}")
            sleep(0.5)
            self.__connect(retry - 1)

    def get_conn(self, force_reconnect=False) -> rpyc.core.protocol.Connection | None:
        """
        Get a rpyc connection. Returns None if fails to connect
        """
        if force_reconnect or self.conn is None:
            self.__connect()
        return self.conn
