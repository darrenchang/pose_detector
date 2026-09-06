import functools


from pose import Pose as P
from flask_restx import Model as SwaggerModel
from flask_restx import fields


class Model:
    def __init__(self) -> None:
        pass

    @functools.cached_property
    def detail(self):
        return SwaggerModel(
            "Detail",
            {
                "detail": fields.String(example="some random details"),
            },
        )

    @functools.cached_property
    def landmark_pose(self):
        return SwaggerModel(
            "LandmarkPose",
            {
                "index": fields.Integer(example=0),
                "name": fields.String(example="nose", default="", enum=P.Pose.landmark_map),
                "x": fields.Float(example=0.01, default=0),
                "y": fields.Float(example=0.01, default=0),
                "z": fields.Float(example=0.01, default=0),
                "visibility": fields.Float(example=0.898989),
            },
        )

    @functools.cached_property
    def landmark_hand(self):
        return SwaggerModel(
            "LandmarkHand",
            {
                "index": fields.Integer(example=0),
                "name": fields.String(example="wrist", default="", enum=P.Hand.landmark_map),
                "x": fields.Float(example=0.01, default=0),
                "y": fields.Float(example=0.01, default=0),
                "z": fields.Float(example=0.01, default=0),
                "visibility": fields.Float(example=0.898989),
            },
        )

    @functools.cached_property
    def landmark_hands(self):
        return SwaggerModel(
            "LandmarkHands",
            {
                "left": fields.List(fields.Nested(self.landmark_hand), default=[]),
                "right": fields.List(fields.Nested(self.landmark_hand), default=[]),
            },
        )

    @functools.cached_property
    def gesture_hand(self):
        return SwaggerModel(
            "GestureHand",
            {
                "left": fields.String(example="unknown", default="", enum=list(P.Hand.gesture_map.values())),
                "right": fields.String(example="closed_fist", default="", enum=list(P.Hand.gesture_map.keys())),
            },
        )

    @functools.cached_property
    def landmarks(self):
        return SwaggerModel(
            "Landmarks",
            {
                "pose_landmarks": fields.List(fields.Nested(self.landmark_pose), default=[]),
                "hand_landmarks": fields.Nested(self.landmark_hands),
                "hand_gestures": fields.Nested(self.gesture_hand),
            },
        )
