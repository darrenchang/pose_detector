from flask import Flask
from flask_socketio import SocketIO as FlaskSocketIO
from socketio import RedisManager

from pose.Logger import Logger

logger = Logger(__file__).get_logger()


class SocketIO:
    def __init__(self, redis_url: str, app: Flask = None, channel: str = "general"):
        self.channel = channel
        self.socketio: FlaskSocketIO = FlaskSocketIO(
            app or Flask(__name__),
            cors_allowed_origins="*",
            path="/socket.io",
            client_manager=RedisManager(redis_url, write_only=False, channel=channel),
        )

    def get_socketio(self):
        return self.socketio
