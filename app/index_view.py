from flask import redirect
from flask_appbuilder import BaseView, expose


class DashboardIndexView(BaseView):
    """Página de inicio: redirige al panel de control."""

    route_base = "/"
    default_view = "index"

    @expose("/")
    def index(self):
        return redirect("/dashboard/")
