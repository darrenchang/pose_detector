import atexit
import os
from multiprocessing.util import _exit_function

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


def post_worker_init(worker):
    atexit.unregister(_exit_function)


def worker_exit(server, worker):
    server.kill_worker(worker.pid, 3)
