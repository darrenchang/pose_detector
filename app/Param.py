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
            location="query",
            help="The id of the camera",
            type=str,
            required=True,
        )
        return parser
