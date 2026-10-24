import json
import os
import time

from flask import make_response, request
from flask_restx import Namespace, Resource, marshal
from rpyc.utils.factory import unix_connect

from Model import Model
from Param import Param
from pose.Logger import Logger
from pose.SocketIoClient import SocketIoClient

logger = Logger(__file__).get_logger()

# Saved landmark snapshots go here (app/src/poses/).
POSES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poses")

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
