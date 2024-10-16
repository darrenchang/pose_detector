import views
from PoseApp import PoseApp


pose_app = PoseApp()
api_prefix = pose_app.get_api_prefix()
app = pose_app.get_app()
api = pose_app.get_api()


# API registry
api.add_namespace(views.ns_base, path=f"/{views.ns_base.name}")
api.add_namespace(views.ns_info, path=f"/{views.ns_info.name}")
