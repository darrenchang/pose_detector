import json
import os
import signal
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event, Lock, Thread
from time import perf_counter

import cv2
import mediapipe as mp
import numpy as np
import requests
import rpyc
from flask_restx import Namespace, marshal
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from rpyc.utils.server import ThreadedServer

from Model import Model
from pose.Camera import Camera
from pose.Logger import Logger
from pose.RedisClient import RedisClient
from pose.SocketIO import SocketIO

logger = Logger(__file__).get_logger()


class Pose:
    landmark_map = [
        # pose landmarks diagram:
        # https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker#pose_landmarker_model
        # NOTE: The order of the items must match the landmarker model
        # head
        "nose",
        "leftEyeInner",
        "leftEye",
        "leftEyeOuter",
        "ghtEyeInner",
        "rightEye",
        "rightEyeOuter",
        "leftEar",
        "rightEar",
        "mouthLeft",
        "mouthRight",
        # body
        "leftShoulder",
        "rightShoulder",
        "leftElbow",
        "rightElbow",
        "leftWrist",
        "rightWrist",
        "leftPinky",
        "rightPinky",
        "leftIndex",
        "rightIndex",
        "leftThumb",
        "rightThumb",
        "leftHip",
        "rightHip",
        "leftKnee",
        "rightKnee",
        "leftAnkle",
        "rightAnkle",
        "leftHeel",
        "rightHeel",
        "leftFootIndex",
        "rightFootIndex",
    ]

    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        # landmarker_model_bundle can be ["light", "full", "heavy"]
        landmarker_model_bundle = "full"
        self.download_model(output_path=self.current_dir, landmarker_model_bundle=landmarker_model_bundle)
        self.base_options = python.BaseOptions(
            model_asset_path=f"{self.current_dir}/pose_landmarker_{landmarker_model_bundle}.task",
        )
        self.options = vision.PoseLandmarkerOptions(
            base_options=self.base_options,
            output_segmentation_masks=True,
        )
        self.recognizer = vision.PoseLandmarker.create_from_options(self.options)
        # Latest inference result (list of 33 landmark dicts, or [] if nobody is in frame)
        self.landmarks = []

    def inference(self, im, store: bool = True):
        """Run pose detection on an RGB frame and return the landmarks.

        With ``store`` (the default) the result also becomes ``self.landmarks``,
        the live value the camera stream publishes; one-off requests such as a
        single uploaded image pass ``store=False`` so they never show up there.
        """
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=im)
        results = self.recognizer.detect(mp_image)
        landmarks = []
        if len(results.pose_landmarks) > 0:
            for i, landmark in enumerate(results.pose_landmarks[0]):
                landmarks.append(
                    {
                        "index": i,
                        "name": self.landmark_map[i],
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility,
                    }
                )
        if store:
            self.landmarks = landmarks
        return landmarks

    def download_model(self, output_path: str, landmarker_model_bundle: str):
        gesture_recognizer_model_url = (
            "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
            f"pose_landmarker_{landmarker_model_bundle}/float16/latest/"
            f"pose_landmarker_{landmarker_model_bundle}.task"
        )
        model_file = f"{output_path}/pose_landmarker_{landmarker_model_bundle}.task"
        if Path(model_file).exists():
            logger.info(
                f"The pose_landmarker file {model_file} is found. Skipping download."
            )
            return
        session = requests.Session()
        with session.get(gesture_recognizer_model_url, stream=True) as r:
            if r.status_code == 200:
                logger.info("Downloading the pose_landmarker model...")
                with open(model_file, "wb") as fd:
                    for chunk in r.iter_content(chunk_size=16 * 1024):
                        fd.write(chunk)
            else:
                logger.warning(
                    f"Failed to download pose_landmarker model. HTTP status code: {r.status_code}"
                )
        return


class Hand:
    landmark_map = [
        # hand landmarks diagram:
        # https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker
        # NOTE: The order of the items must match the landmarker model
        "wrist",
        "thumb_cmc",
        "thumb_mcp",
        "thumb_ip",
        "thumb_tip",
        "index_finger_mcp",
        "index_finger_pip",
        "index_finger_dip",
        "index_finger_tip",
        "middle_finger_mcp",
        "middle_finger_pip",
        "middle_finger_dip",
        "middle_finger_tip",
        "ring_finger_mcp",
        "ring_finger_pip",
        "ring_finger_dip",
        "ring_finger_tip",
        "pinky_mcp",
        "pinky_pip",
        "pinky_dip",
        "pinky_tip",
    ]
    gesture_map = {
        "Pointing_Up": "pointing_up",
        "Open_Palm": "open_palm",
        "Closed_Fist": "closed_fist",
        "Thumb_Down": "thumb_down",
        "Thumb_Up": "thumb_up",
        "Victory": "victory",
        "ILoveYou": "i_love_you",
        "None": "unknown",
    }

    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.download_model(output_path=self.current_dir)
        self.base_options = python.BaseOptions(
            model_asset_path=f"{self.current_dir}/gesture_recognizer.task"
        )
        self.options = vision.GestureRecognizerOptions(
            base_options=self.base_options, num_hands=2
        )
        # self.options = vision.GestureRecognizerOptions(base_options=self.base_options, num_hands=2)
        self.recognizer = vision.GestureRecognizer.create_from_options(self.options)
        # Latest inference results, keyed by "left"/"right"
        self.landmarks = {"left": [], "right": []}
        self.gestures = {"left": "", "right": ""}

    def inference(self, im, store: bool = True):
        """Run hand detection on an RGB frame and return ``(landmarks, gestures)``.

        As with ``Pose.inference``, ``store=False`` keeps a one-off result out
        of the live ``self.landmarks`` / ``self.gestures``.
        """
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=im)
        results = self.recognizer.recognize(image)
        landmarks = {
            "left": [],
            "right": [],
        }
        gestures = {
            "left": "",
            "right": "",
        }
        for i, hand in enumerate(results.handedness):
            hand_name = hand[0].display_name.lower()
            gestures[hand_name] = self.gesture_map.get(
                results.gestures[i][0].category_name, "unknown"
            )
            for k, landmark in enumerate(results.hand_world_landmarks[i]):
                landmarks[hand_name].append(
                    {
                        "index": k,
                        "name": self.landmark_map[k],
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility,
                    }
                )
        if store:
            self.landmarks = landmarks
            self.gestures = gestures
        return landmarks, gestures

    @staticmethod
    def download_model(output_path):
        gesture_recognizer_model_url = (
            "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/latest/"
            "gesture_recognizer.task"
        )
        model_file = f"{output_path}/gesture_recognizer.task"
        if Path(model_file).exists():
            logger.info(
                f"The gesture_recognizer file {model_file} is found. Skipping download."
            )
            return
        session = requests.Session()
        with session.get(gesture_recognizer_model_url, stream=True) as r:
            if r.status_code == 200:
                logger.info("Downloading the gesture_recognizer model...")
                with open(model_file, "wb") as fd:
                    for chunk in r.iter_content(chunk_size=16 * 1024):
                        fd.write(chunk)
            else:
                logger.warning(
                    f"Failed to download gesture_recognizer model. HTTP status code: {r.status_code}"
                )
        return


class RpcService(rpyc.Service):
    def __init__(self, redis_server_sock: str, cam: str, socketio_channel: str):
        self.pose = Pose()
        self.hand = Hand()
        self.fps = 0
        self.redis_client = RedisClient(server_sock=redis_server_sock)
        self.socketio = SocketIO(
            self.redis_client.get_connection_url(), channel=socketio_channel
        ).get_socketio()
        model: Model = Model()
        ns_base = Namespace("base", "Namespace for registering models")
        self.model_landmarks = ns_base.model(model.landmarks.name, model.landmarks)
        # The camera reads frames on its own thread and keeps the newest one on
        # camera.frame; nothing here ever touches cv2.VideoCapture directly.
        self.camera = Camera(cam)
        # Pose and hand detection are independent and both release the GIL
        # inside mediapipe, so they run concurrently on two worker threads;
        # the slower (pose) model then sets the pace instead of their sum.
        self._inference_pool = ThreadPoolExecutor(
            max_workers=2, thread_name_prefix="inference"
        )
        # The mediapipe recognizers are not safe to call concurrently on the
        # same instance, so the camera stream and single-image RPC requests
        # take turns.
        self._inference_lock = Lock()
        # Set by shutdown(); every background loop here watches it. The
        # threads are daemons so a stuck one can never keep the process alive.
        self._stopping = Event()
        self._landmark_thread = Thread(
            target=self.landmark_runner, name="landmark-runner", daemon=True
        )
        self._landmark_thread.start()
        self._fps_thread = Thread(
            target=self.display_fps,
            kwargs={"interval": 5},
            name="fps-logger",
            daemon=True,
        )
        self._fps_thread.start()

    def inference(self, frame=None):
        """Run pose + hand detection on a frame and keep the results on
        self.pose / self.hand. Defaults to the camera's latest frame."""
        if frame is None:
            frame = self.camera.frame
        if frame is None or self._stopping.is_set():
            # No frame captured yet, or we are shutting down
            return
        self._run_models(frame, store=True)

    def _run_models(self, frame, store: bool):
        """Run both models on a BGR frame and return
        ``(pose_landmarks, hand_landmarks, hand_gestures)``."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        with self._inference_lock:
            pose_job = self._inference_pool.submit(self.pose.inference, rgb, store)
            hand_job = self._inference_pool.submit(self.hand.inference, rgb, store)
            pose_landmarks = pose_job.result()
            hand_landmarks, hand_gestures = hand_job.result()
        return pose_landmarks, hand_landmarks, hand_gestures

    def landmark_runner(self):
        """Infer on every new camera frame and publish the landmarks."""
        for frame in self.camera.frames():
            s = perf_counter()
            self.inference(frame)
            if self._stopping.is_set():
                break
            self.socketio.emit(
                "landmarks",
                marshal(
                    {
                        "pose_landmarks": self.pose.landmarks,
                        "hand_landmarks": self.hand.landmarks,
                        "hand_gestures": self.hand.gestures,
                    },
                    self.model_landmarks,
                ),
                to="host_cam",
                namespace="/api/model/get_landmarks",
            )
            self.fps = 1 / (perf_counter() - s)

    def display_fps(self, interval):
        while not self._stopping.wait(interval):
            logger.info(
                f"FPS: inference {self.fps:.2f} / camera {self.camera.fps:.2f}"
            )

    def shutdown(self):
        """Stop the capture, inference and logging threads in order.

        Releasing the camera ends ``camera.frames()``, which lets the landmark
        thread finish its current frame and return; only then is the inference
        pool shut down, so no work is ever submitted to a closed pool.
        """
        if self._stopping.is_set():
            return
        logger.info("Stopping pose service...")
        self._stopping.set()
        self.camera.release()
        self._landmark_thread.join(timeout=5)
        self._inference_pool.shutdown(wait=True)
        self._fps_thread.join(timeout=1)
        logger.info("Pose service stopped")

    def exposed_inference_image(self, image_bytes: bytes) -> str:
        """RPC: run pose + hand detection on one encoded image (jpg/png/...).

        Returns a JSON string ``{"width", "height", "pose_landmarks",
        "hand_landmarks", "hand_gestures"}``; ``width``/``height`` are 0 if
        the bytes could not be decoded as an image. The live camera results
        are left untouched.
        """
        buf = np.frombuffer(bytes(image_bytes), dtype=np.uint8)
        frame = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        if frame is None or self._stopping.is_set():
            return json.dumps({"width": 0, "height": 0})
        height, width = frame.shape[:2]
        pose_landmarks, hand_landmarks, hand_gestures = self._run_models(
            frame, store=False
        )
        return json.dumps(
            {
                "width": width,
                "height": height,
                "pose_landmarks": pose_landmarks,
                "hand_landmarks": hand_landmarks,
                "hand_gestures": hand_gestures,
            }
        )

    def exposed_get_landmarks(self) -> str:
        """RPC: the most recent pose and hand landmarks, as a JSON string.

        Returned as a string (not a dict) so rpyc hands the caller a plain
        copy instead of a live proxy into this process.
        """
        return json.dumps(
            {
                "pose_landmarks": self.pose.landmarks,
                "hand_landmarks": self.hand.landmarks,
            }
        )


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
        self.socketio_channel = socketio_channel
        self.cam = cam
        self.server = None
        self.service = None
        self.__start_service()

    def __start_service(self):
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
        self.service = RpcService(
            redis_server_sock=self.redis_server_sock,
            cam=self.cam,
            socketio_channel=self.socketio_channel,
        )
        self.server = ThreadedServer(
            self.service,
            socket_path=self.socket_path,
            logger=logger,
        )
        # The launcher stops us with SIGTERM; make it unwind the same way
        # Ctrl+C does (rpyc already turns KeyboardInterrupt into a clean stop)
        signal.signal(signal.SIGTERM, self.__handle_sigterm)
        try:
            # Blocks until Ctrl+C or server.close()
            self.server.start()
        finally:
            self.service.shutdown()
            if os.path.exists(self.socket_path):
                os.remove(self.socket_path)

    def __handle_sigterm(self, signum, frame):
        logger.info("SIGTERM received, stopping pose service...")
        # Closing the listener makes server.start() return, which runs the
        # shutdown in __start_service's finally block
        self.server.close()
