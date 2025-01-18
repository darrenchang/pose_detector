import atexit
import importlib
import os
from multiprocessing import Process
from multiprocessing.util import _exit_function

from redislite import Redis

from pose.Logger import Logger
from pose.Pose import PoseService
from pose.RpcClient import RpcClient

port = 8000
logger = Logger(__file__).get_logger()
bind = f"0.0.0.0:{port}"
worker_class = "gthread"
workers = os.cpu_count()
threads = 2
timeout = 120
worker_connections = 32
keepalive = 60
preload = True
proc_name = "pose"
daemon = False
backlog = 1024
max_requests = 100
max_request_jitter = int(max_requests * 0.2)
graceful_timeout = 5


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
p = Process(target=PoseService, kwargs=pose_service_options, daemon=True)
p.start()

pose_service_client = RpcClient(socket_path=pose_service_sock)


def post_fork(server, worker):
    main_module = importlib.import_module("app_main")
    app = getattr(main_module, "app")
    pose_app = getattr(main_module, "pose_app")
    app.config["REDIS_SERVER_SOCK"] = redis_server_sock
    app.config["POSE_SERVICE_SOCK"] = pose_service_sock
    app.config["PORT"] = port
    pose_app.setup_socketio(channel="general")


def post_worker_init(worker):
    atexit.unregister(_exit_function)


def worker_exit(server, worker):
    server.kill_worker(worker.pid, 3)


def on_exit(server):
    logger.info("Shutting down Redis server...")
    redis_server.shutdown()
