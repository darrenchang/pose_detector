import functools

from flask_restx import reqparse
from werkzeug.datastructures import FileStorage


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
    def inference_image(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "file",
            location="files",
            type=FileStorage,
            help="The image to run pose and hand detection on (jpg, png, bmp, webp)",
            required=True,
        )
        return parser
