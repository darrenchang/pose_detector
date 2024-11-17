from flask import make_response
from flask_restx import Namespace, Resource, marshal

from Model import Model
from pose.Logger import Logger
from pose.RedisClient import RedisClient

logger = Logger(__file__).get_logger()

# Namespaces
ns_base = Namespace("base", "Namespace for registering models")
ns_info = Namespace("info", "All information about Pose")
ns_model = Namespace("model", "Endpoints related to pose model")


# Model registry
model: Model = Model()
model_about = ns_base.model(model.about.name, model.about)


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


@ns_model.response(200, "Landmarks API", model_about)
@ns_model.route("/get_landmarks")
class Landmarks(Resource):
    def get(self):
        redis_client = RedisClient(self.api.app.config.get("REDIS_SERVER_SOCK"))
        with redis_client.get_session() as redis_session:
            landmarks = redis_session.get("landmarks")
        logger.info(landmarks)
        return make_response(
            marshal(
                {
                    "detail": "some random stuff here...",
                },
                model_about,
            ),
            200,
        )
