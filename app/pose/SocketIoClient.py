import threading

import socketio


class SocketIoClient:
    def __init__(self, port: str, namespace: str, event_name: str, sub_data: dict()):
        self.url = f"http://localhost:{port}{namespace}"
        self.namespace = namespace
        self.event_name = event_name
        self.event_received = threading.Event()
        self.socketio = socketio.Client()
        self.socketio.connect(
            self.url,
            transports=["websocket"],
            namespaces=[namespace],
        )
        self.socketio.emit(
            "subscribe",
            sub_data,
            namespace=namespace,
        )
        # self.event_received = threading.Event()
        self.state = {
            "landmarks": [],
        }
        self.register_socketio_events(namespace)

    def register_socketio_events(self, namespace: str):
        @self.socketio.on(self.event_name, namespace=self.namespace)
        def handle_event(data):
            self.state["landmarks"] = data
            self.event_received.set()

    def get_one(self):
        self.event_received.wait(3)
        self.socketio.disconnect()
        return self.state
