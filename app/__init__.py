from flask import Flask
from .extensions import appbuilder, db

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")

    db.init_app(app)

    with app.app_context():
        # 1. Primero importar modelos (registra las tablas en SQLAlchemy)
        from . import models  # noqa: F401

        # 2. Luego inicializar appbuilder
        appbuilder.init_app(app, db.session)

        # 3. Crear tablas en la base de datos
        db.create_all()

        # 4. Por último importar vistas
        from . import views  # noqa: F401

    return app