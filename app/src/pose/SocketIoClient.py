import threading

import socketio


class SocketIoClient:
    def __init__(self, port: str, namespace: str, event_name: str, sub_data: dict()):
        self.url = f"http://localhost:{port}{namespace}"
        self.namespace = namespace
        self.event_name = event_name
        self.event_received = threading.Event()
        self.data = None
        self.socketio = socketio.Client()
        # Register the handler before subscribing so no event is missed in the
        # window between connecting and listening
        self.register_socketio_events(namespace)
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

    @staticmethod
    def _has_landmarks(data) -> bool:
        if not data:
            return False
        if data.get("pose_landmarks"):
            return True
        hands = data.get("hand_landmarks") or {}
        return bool(hands.get("left") or hands.get("right"))

    def register_socketio_events(self, namespace: str):
        @self.socketio.on(self.event_name, namespace=self.namespace)
        def handle_event(data):
            # Always keep the latest frame so we can still return an empty
            # result when nobody is in view
            self.data = data
            # Only stop once we have a frame that actually contains landmarks;
            # individual frames often have no detection even when a subject is
            # present, so grabbing the very first event is unreliable
            if self._has_landmarks(data):
                self.event_received.set()
                self.socketio.disconnect()

    def get_one(self, timeout: float = 3.0):
        self.event_received.wait(timeout)
        if self.socketio.connected:
            self.socketio.disconnect()
        return self.data
