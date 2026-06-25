from flask import Flask
from sqlalchemy import inspect, text

from .extensions import appbuilder, db


def _ensure_payment_columns():
    inspector = inspect(db.engine)
    if not inspector.has_table("cliente"):
        return

    cliente_columns = {col["name"] for col in inspector.get_columns("cliente")}
    if "monto_pago" not in cliente_columns:
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE cliente ADD COLUMN monto_pago FLOAT"))
    if "metodo_pago" not in cliente_columns:
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE cliente ADD COLUMN metodo_pago VARCHAR(50)"))

    if inspector.has_table("pago"):
        pago_columns = {col["name"] for col in inspector.get_columns("pago")}
        if "cliente_id" not in pago_columns:
            with db.engine.begin() as conn:
                conn.execute(text("ALTER TABLE pago ADD COLUMN cliente_id INTEGER"))

        if "reserva_id" in pago_columns:
            reserva_col = next(col for col in inspector.get_columns("pago") if col["name"] == "reserva_id")
            if not reserva_col.get("nullable", False):
                dialect = db.engine.dialect.name
                if dialect == "mysql":
                    with db.engine.begin() as conn:
                        conn.execute(text("ALTER TABLE pago MODIFY reserva_id INTEGER NULL"))
                elif dialect == "sqlite":
                    with db.engine.begin() as conn:
                        conn.execute(text("CREATE TABLE pago_new (id INTEGER, monto FLOAT NOT NULL, metodo VARCHAR(50) NOT NULL, fecha DATE NOT NULL, reserva_id INTEGER, cliente_id INTEGER, FOREIGN KEY(reserva_id) REFERENCES reserva(id), FOREIGN KEY(cliente_id) REFERENCES cliente(id))"))
                        conn.execute(text("INSERT INTO pago_new (id, monto, metodo, fecha, reserva_id, cliente_id) SELECT id, monto, metodo, fecha, reserva_id, cliente_id FROM pago"))
                        conn.execute(text("DROP TABLE pago"))
                        conn.execute(text("ALTER TABLE pago_new RENAME TO pago"))


def _sync_role_permissions(role_name, permission_pairs):
    """Create/update a role so it matches the expected permission set."""
    sm = appbuilder.sm
    role = sm.add_role(role_name)
    pvm_target = []
    for perm_name, view_name in set(permission_pairs):
        pvm = sm.find_permission_view_menu(perm_name, view_name)
        if pvm:
            pvm_target.append(pvm)

    # Reemplaza el conjunto completo para mantener consistencia y evitar drift.
    role.permissions = pvm_target

    db.session.commit()


def _ensure_security_roles():
    sm = appbuilder.sm

    # Corrige un rol mal escrito existente sin perder permisos.
    wrong_role = sm.find_role("Superviosr")
    if wrong_role:
        supervisor = sm.add_role("Supervisor")
        for pvm in list(wrong_role.permissions):
            sm.add_permission_role(supervisor, pvm)
        db.session.delete(wrong_role)
        db.session.commit()

    recepcionista_permissions = [
        ("menu_access", "Inicio"),
        ("menu_access", "Gestión"),
        ("menu_access", "Clientes"),
        ("menu_access", "Reservas"),
        ("menu_access", "Pagos"),
        ("menu_access", "Vista Visual"),
        ("can_list", "ClienteView"),
        ("can_show", "ClienteView"),
        ("can_add", "ClienteView"),
        ("can_edit", "ClienteView"),
        ("can_list", "ReservaView"),
        ("can_show", "ReservaView"),
        ("can_add", "ReservaView"),
        ("can_edit", "ReservaView"),
        ("can_list", "PagoView"),
        ("can_show", "PagoView"),
        ("can_add", "PagoView"),
        ("can_edit", "PagoView"),
    ]

    supervisor_permissions = [
        ("menu_access", "Inicio"),
        ("menu_access", "Reportes"),
        ("menu_access", "Gráficos"),
        ("menu_access", "Clientes"),
        ("menu_access", "Reservas"),
        ("menu_access", "Pagos"),
        ("menu_access", "Vista Visual"),
        ("can_list", "ClienteView"),
        ("can_show", "ClienteView"),
        ("can_list", "ReservaView"),
        ("can_show", "ReservaView"),
        ("can_list", "PagoView"),
        ("can_show", "PagoView"),
        ("can_list", "HabitacionView"),
        ("can_show", "HabitacionView"),
    ]

    _sync_role_permissions("Recepcionista", recepcionista_permissions)
    _sync_role_permissions("Supervisor", supervisor_permissions)

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")

# Redirigir al dashboard después del login
    app.config["FAB_INDEX_VIEW"] = "app.index_view.DashboardIndexView"

    db.init_app(app)

    with app.app_context():
        # 1. Importar modelos
        from . import models  # noqa: F401

        # 2. Inicializar appbuilder
        appbuilder.init_app(app, db.session)

        # 3. Asegurar columnas de pago en la base de datos
        _ensure_payment_columns()

        # 4. Crear tablas
        db.create_all()

        # 5. Filtro enumerate para Jinja2
        app.jinja_env.filters['enumerate'] = enumerate

        # 5. Importar vistas
        from . import views  # noqa: F401

        # 6. Estandarizar roles base
        _ensure_security_roles()

    return app
