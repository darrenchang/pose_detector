from flask import make_response
from flask_restx import Namespace, Resource, marshal

from Model import Model
from pose.Logger import Logger
from pose.SocketIoClient import SocketIoClient

logger = Logger(__file__).get_logger()

# Namespaces
ns_base = Namespace("base", "Namespace for registering models")
ns_info = Namespace("info", "All information about Pose")
ns_model = Namespace("model", "Endpoints related to pose model")


# Model registry
model: Model = Model()
model_about = ns_base.model(model.about.name, model.about)
ns_base.model(model.landmark.name, model.landmark)
model_landmarks = ns_base.model(model.landmarks.name, model.landmarks)


@ns_info.response(200, "About the API", model_about)
@ns_info.route("/about")
class Login(Resource):
    def get(self):
        return make_response(
            marshal(
                {
                    "detail": "some random stuff here...",
                },
                model_about,
            ),
            200,
        )


@ns_model.response(200, "Get landmarks", model_landmarks)
@ns_model.route("/get_landmarks")
class GetLandmarks(Resource):
    def get(self):
        landmarks = SocketIoClient(
            port=self.api.app.config.get("PORT"),
            namespace="/api/model/get_landmarks",
            event_name="pose_landmarks",
            sub_data={"cam_id": "host_cam"},
        ).get_one()
        return make_response(
            marshal(
                {
                    "pose_landmarks": landmarks.get("landmarks"),
                },
                model_landmarks,
            ),
            200,
        )
