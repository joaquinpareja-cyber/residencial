from flask import Flask
from .extensions import appbuilder, db

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")

    db.init_app(app)

    with app.app_context():
        # 1. Importar modelos
        from . import models  # noqa: F401

        # 2. Inicializar appbuilder
        appbuilder.init_app(app, db.session)

        # 3. Crear tablas
        db.create_all()

        # 4. Agregar filtro enumerate a Jinja2
        app.jinja_env.filters['enumerate'] = enumerate

        # 5. Importar vistas
        from . import views  # noqa: F401

    return app
