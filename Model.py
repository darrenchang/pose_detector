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
