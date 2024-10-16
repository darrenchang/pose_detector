import atexit
import os
import subprocess
from multiprocessing.util import _exit_function

import psutil

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


# Run pose detection process in the background
proc = subprocess.Popen(["python", "pose/Pose.py"], start_new_session=True)


# Make sure Pose process is killed when the main app quits
def cleanup():
    try:
        parent = psutil.Process(proc.pid)
        for child in parent.children(recursive=True):  # Recursively find child processes
            child.terminate()
        parent.terminate()
    except psutil.NoSuchProcess:
        pass  # Process already terminated


atexit.register(cleanup)


def post_worker_init(worker):
    from app_main import app

    app.config["SOME_CUSTOM_VALUE"] = "hello"
    atexit.unregister(_exit_function)


def worker_exit(server, worker):
    server.kill_worker(worker.pid, 3)
