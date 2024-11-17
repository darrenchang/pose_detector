from flask import Flask, request
from flask_socketio import SocketIO as FlaskSocketIO
from flask_socketio import emit, join_room, leave_room, send
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
        self.register_socketio_events()

    def register_socketio_events(self):
        @self.socketio.on("connect")
        def handle_connect():
            sid = request.sid
            logger.info(f"[Channel: {self.channel}] Client connected {sid}")
            emit("response", {"message": "Connected to the server!"})

        @self.socketio.on("disconnect")
        def handle_disconnect():
            sid = request.sid
            logger.info(f"[Channel: {self.channel}] Client disconnected {sid}")

        @self.socketio.on('message')
        def handle_message(message):
            send(message)

    def get_socketio(self):
        return self.socketio
