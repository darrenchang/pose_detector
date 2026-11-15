import json
import os
import time

from flask import make_response, request
from flask_restx import Namespace, Resource, marshal
from rpyc.utils.factory import unix_connect
from werkzeug.utils import secure_filename

from Model import Model
from Param import Param
from pose.Logger import Logger
from pose.SocketIoClient import SocketIoClient

logger = Logger(__file__).get_logger()

# Saved landmark snapshots go here (app/src/poses/).
POSES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poses")
# Inference results for uploaded images go here (app/src/poses_data/).
POSES_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poses_data")
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "webp"}

# Namespaces
ns_base = Namespace("base", "Namespace for registering models")
ns_info = Namespace("info", "All information about Pose")
ns_model = Namespace("model", "Endpoints related to pose model")

param: Param = Param()

# Model registry
model: Model = Model()
model_detail = ns_base.model(model.detail.name, model.detail)
ns_base.model(model.landmark_pose.name, model.landmark_pose)
ns_base.model(model.landmark_hands.name, model.landmark_hands)
ns_base.model(model.landmark_hand.name, model.landmark_hand)
ns_base.model(model.gesture_hand.name, model.gesture_hand)
model_landmarks = ns_base.model(model.landmarks.name, model.landmarks)
ns_base.model(model.image_info.name, model.image_info)
model_inference_image = ns_base.model(model.inference_image.name, model.inference_image)


@ns_info.response(200, "About the API", model_detail)
@ns_info.route("/about")
class Login(Resource):
    def get(self):
        return make_response(
            marshal(
                {
                    "detail": "some random stuff here...",
                },
                model_detail,
            ),
            200,
        )


@ns_model.expect(param.get_landmarks)
@ns_model.response(200, "Get landmarks", model_landmarks)
@ns_model.route("/get_landmarks")
class GetLandmarks(Resource):
    @ns_model.doc(
        summary="⚡ SocketIO supported",
        description=(
            "##SocketIO\n"
            "**Messages:**\n"
            "- `subscribe` to pose landmark updates. Data: `{\"cam_id\": \"host_cam\"}`\n"
            "- `unsubscribe` to pose landmark updates. Data: `{\"cam_id\": \"host_cam\"}`\n"
            "- `landmarks` - listen. Data: `#definitions/LandmarksLandmarks`\n"
        ),
    )
    def get(self):
        cam_id = request.args.get("cam_id")
        landmarks = SocketIoClient(
            port=self.api.app.config.get("PORT"),
            namespace="/api/model/get_landmarks",
            event_name="landmarks",
            sub_data={"cam_id": cam_id},
        ).get_one()
        return make_response(
            marshal(
                landmarks,
                model_landmarks,
            ),
            200,
        )


def fetch_current_landmarks(pose_service_sock: str) -> dict:
    """Ask the pose service process for its latest Pose/Hand landmarks."""
    conn = unix_connect(pose_service_sock, config={"sync_request_timeout": 5})
    try:
        return json.loads(conn.root.get_landmarks())
    finally:
        conn.close()


@ns_model.response(200, "Save landmarks", model_detail)
@ns_model.response(400, "No pose detected", model_detail)
@ns_model.response(409, "A snapshot was already saved this second", model_detail)
@ns_model.response(500, "Failed to write the file", model_detail)
@ns_model.response(503, "Pose service unavailable", model_detail)
@ns_model.route("/save_landmarks")
class SaveLandmarks(Resource):
    @ns_model.doc(
        summary="Save the current landmarks to storage",
        description=(
            "Snapshots the pose service's current `Pose.landmarks` and "
            "`Hand.landmarks` and saves them as "
            "`app/src/poses/<unix timestamp>.json` in the form "
            "`{\"pose_landmarks\": [...], \"hand_landmarks\": {\"left\": [...], \"right\": [...]}}`."
        ),
    )
    def post(self):
        def fail(msg: str, status: int):
            logger.warning(msg)
            return make_response(marshal({"detail": msg}, model_detail), status)

        try:
            data = fetch_current_landmarks(self.api.app.config.get("POSE_SERVICE_SOCK"))
        except Exception as e:
            logger.warning(e)
            return fail("Pose service unavailable", 503)
        if not data.get("pose_landmarks"):
            return fail("No pose detected, nothing to save", 400)

        os.makedirs(POSES_DIR, exist_ok=True)
        filename = f"{int(time.time())}.json"
        path = os.path.join(POSES_DIR, filename)
        try:
            # O_EXCL: never overwrite a snapshot taken earlier in the same second.
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError:
            return fail(f"poses/{filename} already exists, try again in a second", 409)
        except OSError as e:
            logger.error(f"Failed to save landmarks to {path}: {e}")
            return fail("Failed to save landmarks", 500)
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            logger.error(f"Failed to save landmarks to {path}: {e}")
            return fail("Failed to save landmarks", 500)

        logger.info(f"Saved landmarks to {path}")
        return make_response(
            marshal({"detail": f"saved poses/{filename}"}, model_detail),
            200,
        )


def inference_image_bytes(pose_service_sock: str, image_bytes: bytes) -> dict:
    """Ask the pose service process to run both models on one encoded image."""
    # A large photo takes a moment to ship over the socket and decode on top
    # of the inference itself, so allow well over the streaming budget.
    conn = unix_connect(pose_service_sock, config={"sync_request_timeout": 60})
    try:
        return json.loads(conn.root.inference_image(image_bytes))
    finally:
        conn.close()


@ns_model.expect(param.inference_image)
@ns_model.response(200, "Inference result", model_inference_image)
@ns_model.response(400, "No image, unsupported type or undecodable image", model_detail)
@ns_model.response(500, "Failed to write the result file", model_detail)
@ns_model.response(503, "Pose service unavailable", model_detail)
@ns_model.route("/inference_image")
class InferenceImage(Resource):
    @ns_model.doc(
        summary="Run pose and hand detection on one uploaded image",
        description=(
            "Upload an image as multipart form field `file`. The pose service "
            "runs both models on it and the result is stored as "
            "`app/src/poses_data/<unix ms>_<filename>.json` in the form "
            "`{\"image\": {...}, \"pose_landmarks\": [...], "
            "\"hand_landmarks\": {\"left\": [...], \"right\": [...]}, "
            "\"hand_gestures\": {...}}`. The same document is returned, plus "
            "`saved_as`. The live camera stream is not affected."
        ),
    )
    def post(self):
        def fail(msg: str, status: int):
            logger.warning(msg)
            return make_response(marshal({"detail": msg}, model_detail), status)

        file = request.files.get("file")
        if file is None or not file.filename:
            return fail("No image file provided", 400)
        filename = secure_filename(file.filename) or "image"
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in IMAGE_EXTENSIONS:
            return fail(
                f"Unsupported file type '{ext}', expected one of "
                f"{', '.join(sorted(IMAGE_EXTENSIONS))}",
                400,
            )
        image_bytes = file.read()
        if not image_bytes:
            return fail("The uploaded file is empty", 400)

        try:
            result = inference_image_bytes(
                self.api.app.config.get("POSE_SERVICE_SOCK"), image_bytes
            )
        except Exception as e:
            logger.warning(e)
            return fail("Pose service unavailable", 503)
        if not result.get("width"):
            return fail(f"Could not decode '{filename}' as an image", 400)

        data = {
            "image": {
                "filename": filename,
                "width": result["width"],
                "height": result["height"],
            },
            "pose_landmarks": result.get("pose_landmarks", []),
            "hand_landmarks": result.get("hand_landmarks", {"left": [], "right": []}),
            "hand_gestures": result.get("hand_gestures", {"left": "", "right": ""}),
        }

        os.makedirs(POSES_DATA_DIR, exist_ok=True)
        stem = filename.rsplit(".", 1)[0]
        out_name = f"{int(time.time() * 1000)}_{stem}.json"
        path = os.path.join(POSES_DATA_DIR, out_name)
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            logger.error(f"Failed to save inference result to {path}: {e}")
            return fail("Failed to save the inference result", 500)
        logger.info(f"Saved inference result for {filename} to {path}")

        data["saved_as"] = f"poses_data/{out_name}"
        return make_response(marshal(data, model_inference_image), 200)
