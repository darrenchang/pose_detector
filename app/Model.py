import functools

from flask_restx import Model as SwaggerModel
from flask_restx import fields


class Model:
    def __init__(self) -> None:
        pass

    @functools.cached_property
    def about(self):
        return SwaggerModel(
            "About",
            {
                "detail": fields.String(example="some random details"),
            },
        )

    @functools.cached_property
    def landmark(self):
        return SwaggerModel(
            "Landmark",
            {
                "x": fields.Float(example=0.01, default=0),
                "y": fields.Float(example=0.01, default=0),
                "z": fields.Float(example=0.01, default=0),
            },
        )

    @functools.cached_property
    def landmarks(self):
        return SwaggerModel(
            "Landmarks",
            {
                "pose_landmarks": fields.List(fields.Nested(self.landmark)),
            },
        )
