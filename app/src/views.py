import json
import os
import re
from datetime import datetime

from flask import make_response, request
from flask_restx import Namespace, Resource, marshal

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


@ns_model.expect(param.save_landmarks)
@ns_model.response(200, "Save landmarks", model_detail)
@ns_model.response(400, "Invalid request", model_detail)
@ns_model.response(500, "Failed to write the file", model_detail)
@ns_model.route("/save_landmarks")
class SaveLandmarks(Resource):
    @ns_model.doc(
        summary="Save the landmarks to storage",
        description=(
            "Saves a `Landmarks` object (the same shape `get_landmarks` returns) "
            "as `app/src/poses/<pose_name>_<timestamp>.json`."
        ),
    )
    def post(self):
        args = param.save_landmarks.parse_args()
        pose_name = args["pose_name"]
        landmarks = args["landmarks"]

        def bad_request(msg: str):
            logger.warning(msg)
            return make_response(marshal({"detail": msg}, model_detail), 400)

        # Only keep filesystem-safe characters so the name can't escape POSES_DIR.
        safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", pose_name.strip()).strip("_")
        if not safe_name:
            return bad_request("Invalid pose_name")

        try:
            landmarks_obj = json.loads(landmarks)
        except Exception as e:
            logger.warning(e)
            return bad_request("Invalid landmark json format")
        if not isinstance(landmarks_obj, dict) or not landmarks_obj.get("pose_landmarks"):
            return bad_request("landmarks must be a Landmarks object with non-empty pose_landmarks")

        # Normalise to the documented Landmarks schema (defaults filled, unknown keys dropped).
        data = marshal(landmarks_obj, model_landmarks)

        os.makedirs(POSES_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{safe_name}_{timestamp}.json"
        path = os.path.join(POSES_DIR, filename)
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            logger.error(f"Failed to save landmarks to {path}: {e}")
            return make_response(
                marshal({"detail": "Failed to save landmarks"}, model_detail), 500
            )

        logger.info(f"Saved landmarks for '{pose_name}' to {path}")
        return make_response(
            marshal({"detail": f"saved poses/{filename}"}, model_detail),
            200,
        )
