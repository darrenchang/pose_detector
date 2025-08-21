import atexit
import os
import secrets
import sys
from multiprocessing import Process
from multiprocessing.util import _exit_function

from gunicorn.app.base import BaseApplication
from redislite import Redis

from pose.Logger import Logger
from pose.Pose import PoseService
from PoseApp import PoseApp

logger = Logger(__name__).get_logger()


class StandaloneApplication(BaseApplication):
    """Custom Gunicorn application to load config and app in Python."""

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        # Apply only valid gunicorn settings
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def post_worker_init(worker):
    atexit.unregister(_exit_function)


def worker_exit(server, worker):
    server.kill_worker(worker.pid, 3)


def on_exit_factory(redis_server):
    def on_exit(server):
        logger.info("Shutting down Redis server...")
        redis_server.shutdown()


def get_main_app():
    import views as views

    pose_app = PoseApp()
    app = pose_app.get_app()
    api = pose_app.get_api()
    # API registry
    api.add_namespace(views.ns_base, path=f"/{views.ns_base.name}")
    api.add_namespace(views.ns_info, path=f"/{views.ns_info.name}")
    api.add_namespace(views.ns_model, path=f"/{views.ns_model.name}")
    return pose_app, app


def run_app(
    app_factory,
    options,
    flask_secrete,
    redis_server_sock: str,
    pose_service_sock: str,
    port: str,
):
    pose_app, app = app_factory()
    app.config["REDIS_SERVER_SOCK"] = redis_server_sock
    app.config["POSE_SERVICE_SOCK"] = pose_service_sock
    app.config["PORT"] = port
    app.secret_key = flask_secrete
    pose_app.setup_socketio(channel="general")
    StandaloneApplication(app, options).run()


if __name__ == "__main__":
    logger.info("Starting Pose Detector...")
    sys.dont_write_bytecode = True

    # Launch the background services
    # Setup redis server
    redis_server = Redis(serverconfig={"save": '""', "appendonly": "no"})
    redis_server_sock = redis_server.config_get("unixsocket").get("unixsocket")

    # Run pose detection process in the background
    pose_service_sock = "/tmp/pose.sock"
    pose_service_options = {
        "redis_server_sock": redis_server_sock,
        "cam": os.getenv("VIDEO_SOURCE"),
        "socket_path": pose_service_sock,
        "socketio_channel": "general",
    }
    p = Process(
        target=PoseService,
        kwargs=pose_service_options,
        daemon=True,
    )
    p.start()

    flask_secret = secrets.token_hex(24)
    # Gunicorn setting
    proc_name = "Pose Runtime"
    max_requests = 100
    port = "8000"
    options_main = {
        "bind": f"0.0.0.0:{port}",
        "workers": 1,
        "threads": 8,
        "backlog": 1024,
        "max_requests": max_requests,
        "max_requests_jitter": int(max_requests * 2),
        "worker_class": "gthread",
        "graceful_timeout": 5,
        "loglevel": "error",
        "proc_name": proc_name,
        "daemon": False,
        "timeout": 120,
        "worker_connections": 1024,
        "keepalive": 60,
        "preload": True,
        "post_worker_init": post_worker_init,
        "worker_exit": worker_exit,
        "on_exit": on_exit_factory(redis_server=redis_server),
    }

    # Launch the main WSGI service
    apps = [
        (get_main_app, options_main),
    ]
    processes = []
    for app_factory, opts in apps:
        logger.info(app_factory)
        p = Process(
            target=run_app,
            args=(
                app_factory,
                opts,
                flask_secret,
                redis_server_sock,
                pose_service_sock,
                port,
            ),
        )
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
