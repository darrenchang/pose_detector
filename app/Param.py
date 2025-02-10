import functools

from flask_restx import reqparse


class Param:
    """
    Define the api request data
    """

    def __init__(self) -> None:
        pass

    @functools.cached_property
    def get_landmarks(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "cam_id",
            default="host_cam",
            location="query",
            help="The id of the camera",
            type=str,
            required=True,
        )
        return parser

    @functools.cached_property
    def save_landmarks(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "pose_name",
            default="standing",
            location="form",
            help=(
                "The name for the pose described by the landmarks. Example: "
                "choose one of `['standing', 'sitting', 'lying', 'kneeling', 'all-fours']`, "
                "or anything you can come up with."
            ),
            type=str,
            required=True,
        )
        parser.add_argument(
            "landmarks",
            default="[1,2,3]",
            location="form",
            help="Landmark coordinates",
            type=object,
            required=True,
        )
        return parser
