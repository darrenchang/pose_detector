from flask import Flask, request
from flask_socketio import emit, join_room, leave_room

from pose.SocketIO import SocketIO
from pose.Logger import Logger

logger = Logger(__file__).get_logger()


class SocketIORoutes(SocketIO):
    def __init__(self, redis_url: str, app: Flask = None, channel: str = "general"):
        super().__init__(redis_url, app, channel)
        self.register_socketio_events("/api/model/get_landmarks")

    def register_socketio_events(self, namespace: str):

        @self.socketio.on("connect", namespace=namespace)
        def handle_connect_landmarks():
            sid = request.sid
            logger.debug(f"[Channel: {self.channel}] Client connected to landmarks {sid}")
            emit("response", {"message": "Connected to the server!"})

        @self.socketio.on("disconnect", namespace=namespace)
        def handle_disconnect_landmarks():
            sid = request.sid
            logger.debug(f"[Channel: {self.channel}] Client disconnected from landmarks {sid}")

        @self.socketio.on("subscribe", namespace=namespace)
        def handle_subscribe(data):
            sid = request.sid
            uuid = data.get("cam_id")
            if uuid:
                logger.debug(f"Client {sid} subscribing to room {uuid}...")
                join_room(uuid, sid=sid)
                emit("subscribe", {"message": f"Subscribed to {uuid}"}, room=sid)

        @self.socketio.on("unsubscribe", namespace=namespace)
        def handle_unsubscribe(data):
            sid = request.sid
            uuid = data.get("cam_id")
            if uuid:
                logger.debug(f"Client {sid} unsubscribing from room {uuid}...")
                leave_room(uuid, sid=sid)
                emit("unsubscribe", {"message": f"Unsubscribed from {uuid}"}, room=sid)

        # @self.socketio.on("message")
        # def handle_message(message):
        #     send(message)

    def get_socketio(self):
        return self.socketio
