import json

from flask import make_response, request
from flask_restx import Namespace, Resource, marshal

from Model import Model
from Param import Param
from pose.Logger import Logger
from pose.SocketIoClient import SocketIoClient

logger = Logger(__file__).get_logger()

# Namespaces
ns_base = Namespace("base", "Namespace for registering models")
ns_info = Namespace("info", "All information about Pose")
ns_model = Namespace("model", "Endpoints related to pose model")

param: Param = Param()

# Model registry
model: Model = Model()
model_detail = ns_base.model(model.detail.name, model.detail)
ns_base.model(model.landmark.name, model.landmark)
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
    def get(self):
        """
        SocketIO supported
        SocketIO events:
        - `subscribe` to pose landmark updates. Data: `{"cam_id": "host_cam"}`
        - `unsubscribe` to pose landmark updates. Data: `{"cam_id": "host_cam"}`
        - `pose_landmarks` - listen. Data: `#definitions/LandmarksLandmarks`
        """
        cam_id = request.args.get("cam_id")
        landmarks = SocketIoClient(
            port=self.api.app.config.get("PORT"),
            namespace="/api/model/get_landmarks",
            event_name="pose_landmarks",
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
@ns_model.route("/save_landmarks")
class SaveLandmarks(Resource):
    def post(self):
        """
        Save the landmarks to storage
        """
        pose_name = request.form.get("pose_name", {})
        landmarks = request.form.get("landmarks", {})
        try:
            landmarks_obj = json.loads(landmarks)
            logger.info(pose_name)
            logger.info(landmarks_obj)
        except Exception as e:
            error_msg = "Invalid landmark json format"
            logger.warning(e)
            logger.warning(error_msg)
            return make_response(
                marshal(
                    {"detail": error_msg},
                    model_detail,
                ),
                403,
            )

        return make_response(
            marshal(
                {"detail": "success"},
                model_detail,
            ),
            200,
        )
