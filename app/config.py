import atexit
import importlib
import os
import subprocess
from multiprocessing import Process
from multiprocessing.util import _exit_function

import psutil
from redislite import Redis

from pose.Pose import pose_detect_runner

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
p = Process(target=pose_detect_runner, kwargs={"redis_server_sock": redis_server_sock})
p.start()


def post_worker_init(worker):
    main_module = importlib.import_module("app_main")
    app = getattr(main_module, "app")
    app.config["SOME_CUSTOM_VALUE"] = "hello"
    app.config["REDIS_SERVER_SOCK"] = redis_server_sock
    atexit.unregister(_exit_function)


def worker_exit(server, worker):
    server.kill_worker(worker.pid, 3)
