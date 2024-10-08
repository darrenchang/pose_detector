from flask import make_response
from flask_restx import Namespace, Resource, marshal

from Model import Model

# Namespaces
ns_base = Namespace("base", "Namespace for registering models")
ns_info = Namespace("info", "All information about Pose")


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
