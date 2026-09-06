import os

from flask import Flask
from flask_restx import Api

from flask_session import Session
from pose.Logger import Logger
from pose.RedisClient import RedisClient
from SocketIORoutes import SocketIORoutes

logger = Logger(__file__).get_logger()


class PoseApp:
    def __init__(
        self,
        redis_server_sock: str,
        pose_service_sock: str,
        port: str,
        flask_secret: str,
    ):
        app = Flask(__name__)
        app.secret_key = flask_secret
        app.config["SESSION_TYPE"] = "FileSystem"
        app.config["REDIS_SERVER_SOCK"] = redis_server_sock
        app.config["POSE_SERVICE_SOCK"] = pose_service_sock
        app.config["PORT"] = port
        app.config.setdefault("RESTX_MASK_SWAGGER", False)
        Session(app)
        api_prefix = "/api"
        api = Api(
            app,
            prefix=api_prefix,
            title="Pose",
            description="REST API for pose detection",
            version="",
            doc=False,
        )
        self.app = app
        self.api = api

    def get_app(self):
        return self.app

    def get_api(self):
        return self.api

    def setup_socketio(self, channel: str):
        logger.info(f"Setting up SocketIO on {os.getpid()}")
        redis_client = RedisClient(self.app.config.get("REDIS_SERVER_SOCK"))
        SocketIORoutes(
            redis_client.get_connection_url(), self.app, channel=channel
        ).get_socketio()
