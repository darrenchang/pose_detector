import os
from threading import Thread
from time import perf_counter, sleep

import cv2
import mediapipe as mp
import rpyc
from flask_restx import Namespace, marshal
from rpyc.utils.server import ThreadedServer

from Model import Model
from pose.Logger import Logger
from pose.RedisClient import RedisClient
from pose.SocketIO import SocketIO

logger = Logger(__file__).get_logger()


class Pose:
    # https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker#pose_landmarker_model
    def __init__(self):
        mp_pose = mp.solutions.pose
        pose_options = {
            "static_image_mode": True,
            "min_detection_confidence": 0.5,
            "min_tracking_confidence": 0.5,
            "enable_segmentation": True,
            "model_complexity": 0,
        }
        self.pose = mp_pose.Pose(**pose_options)

    def inference(self, im):
        results = self.pose.process(im)
        landmarks = []
        if results.pose_landmarks is not None:
            for i, landmark in enumerate(results.pose_landmarks.landmark):
                landmarks.append(
                    {
                        "index": i,
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility,
                    }
                )
        return results, landmarks


class RpcService(rpyc.Service):
    def __init__(self, redis_server_sock: str, cam: str, socketio_channel: str):
        self.pose = Pose()
        self.fps = 0
        self.target_fps = 100
        self.frame_duration = 1.0 / self.target_fps
        self.redis_client = RedisClient(server_sock=redis_server_sock)
        self.socketio = SocketIO(self.redis_client.get_connection_url()).get_socketio()
        model: Model = Model()
        ns_base = Namespace("base", "Namespace for registering models")
        self.model_landmarks = ns_base.model(model.landmarks.name, model.landmarks)
        pose_runner = Thread(
            target=self.pose_detect_runner, kwargs={"redis_server_sock": redis_server_sock, "cam": cam}
        )
        pose_runner.start()
        fps_runner = Thread(target=self.display_fps, kwargs={"interval": 5})
        fps_runner.start()

    def pose_detect_runner(self, redis_server_sock: str, cam: int = 0):
        if cam.isdigit():
            # if the input value isdigit, then it's most likely a video cam
            cam = int(cam)
        cap = cv2.VideoCapture(cam)

        if not cap.isOpened():
            logger.warning("Cannot open camera")
            exit()
        while True:
            s = perf_counter()
            ret, img = cap.read()
            if not ret:
                logger.warning("Cannot receive frame")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results, landmarks = self.pose.inference(img2)
            self.socketio.emit(
                "pose_landmarks",
                marshal({"pose_landmarks": landmarks}, self.model_landmarks),
                to="host_cam",
                namespace="/api/model/get_landmarks",
            )
            # Calculate elapsed time
            elapsed_time = perf_counter() - s
            # Sleep for the remaining time to match the target frame duration
            if elapsed_time < self.frame_duration:
                sleep(self.frame_duration - elapsed_time)
            self.fps = 1 / (perf_counter() - s)
        cap.release()
        cv2.destroyAllWindows()

    def display_fps(self, interval):
        while True:
            logger.info(f"FPS: {self.fps:.2f}")
            sleep(interval)


class PoseService:
    def __init__(
        self,
        socket_path: str,
        redis_server_sock: str,
        cam: str,
        socketio_channel: str,
    ) -> None:
        self.socket_path = socket_path
        self.redis_server_sock = redis_server_sock
        self.socketio_channel = socket_path
        self.cam = cam
        self.__start_service()
        self.server = None

    def __start_service(self):
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
        self.server = ThreadedServer(
            RpcService(
                redis_server_sock=self.redis_server_sock,
                cam=self.cam,
                socketio_channel=self.socketio_channel,
            ),
            socket_path=self.socket_path,
            logger=logger,
        )
        self.server.start()
