import logging

from redis import ConnectionPool, StrictRedis, UnixDomainSocketConnection

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self, server_sock: str = "/sock/redis.sock") -> None:
        self.server_sock = server_sock
        self.pool = self._create_pool()

    def get_session(self):
        return StrictRedis(connection_pool=self.pool)

    def _is_redis_available(self, pool):
        try:
            r = StrictRedis(connection_pool=pool)
            r.ping()
            return True
        except Exception:
            logger.warning("Redis connection failed")
            return False

    def _create_pool(self):
        client_name = "Pose"
        pool = ConnectionPool(
            connection_class=UnixDomainSocketConnection,
            path=self.server_sock,
            client_name=client_name,
        )
        self._is_redis_available(pool)
        return pool
