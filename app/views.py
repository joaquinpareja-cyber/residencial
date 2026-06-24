from flask_appbuilder import ModelView, BaseView, expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy import func

from .extensions import appbuilder, db
from .models import (
    TipoHabitacion, Habitacion, Cliente,
    Reserva, Pago, Servicio, ReservaServicio
)


class TipoHabitacionView(ModelView):
    datamodel = SQLAInterface(TipoHabitacion)
    label_columns = {
        "nombre": "Nombre",
        "capacidad": "Capacidad (personas)",
        "descripcion": "Descripción",
    }
    list_columns = ["nombre", "capacidad", "descripcion"]
    add_columns  = ["nombre", "capacidad", "descripcion"]
    edit_columns = ["nombre", "capacidad", "descripcion"]
    show_columns = ["nombre", "capacidad", "descripcion"]


class HabitacionView(ModelView):
    datamodel = SQLAInterface(Habitacion)
    label_columns = {
        "numero": "Número",
        "tipo": "Tipo de habitación",
        "precio_noche": "Precio por noche (Bs)",
        "estado": "Estado",
    }
    list_columns = ["numero", "tipo", "precio_noche", "estado"]
    add_columns  = ["numero", "tipo", "precio_noche", "estado"]
    edit_columns = ["numero", "tipo", "precio_noche", "estado"]
    show_columns = ["numero", "tipo", "precio_noche", "estado"]


class ClienteView(ModelView):
    datamodel = SQLAInterface(Cliente)
    label_columns = {
        "nombre": "Nombre completo",
        "email": "Correo electrónico",
        "telefono": "Teléfono",
    }
    list_columns = ["nombre", "email", "telefono"]
    add_columns  = ["nombre", "email", "telefono"]
    edit_columns = ["nombre", "email", "telefono"]
    show_columns = ["nombre", "email", "telefono"]


class ReservaView(ModelView):
    datamodel = SQLAInterface(Reserva)
    label_columns = {
        "cliente": "Cliente",
        "habitacion": "Habitación",
        "fecha_entrada": "Fecha de entrada",
        "fecha_salida": "Fecha de salida",
        "estado": "Estado",
    }
    list_columns = ["cliente", "habitacion", "fecha_entrada", "fecha_salida", "estado"]
    add_columns  = ["cliente", "habitacion", "fecha_entrada", "fecha_salida", "estado"]
    edit_columns = ["cliente", "habitacion", "fecha_entrada", "fecha_salida", "estado"]
    show_columns = ["cliente", "habitacion", "fecha_entrada", "fecha_salida", "estado"]


class PagoView(ModelView):
    datamodel = SQLAInterface(Pago)
    label_columns = {
        "reserva": "Reserva",
        "monto": "Monto (Bs)",
        "metodo": "Método de pago",
        "fecha": "Fecha",
    }
    list_columns = ["reserva", "monto", "metodo", "fecha"]
    add_columns  = ["reserva", "monto", "metodo", "fecha"]
    edit_columns = ["reserva", "monto", "metodo", "fecha"]
    show_columns = ["reserva", "monto", "metodo", "fecha"]


class ServicioView(ModelView):
    datamodel = SQLAInterface(Servicio)
    label_columns = {
        "nombre": "Nombre del servicio",
        "precio": "Precio (Bs)",
    }
    list_columns = ["nombre", "precio"]
    add_columns  = ["nombre", "precio"]
    edit_columns = ["nombre", "precio"]
    show_columns = ["nombre", "precio"]


class ReservaServicioView(ModelView):
    datamodel = SQLAInterface(ReservaServicio)
    label_columns = {
        "reserva": "Reserva",
        "servicio": "Servicio",
        "cantidad": "Cantidad",
    }
    list_columns = ["reserva", "servicio", "cantidad"]
    add_columns  = ["reserva", "servicio", "cantidad"]
    edit_columns = ["reserva", "servicio", "cantidad"]
    show_columns = ["reserva", "servicio", "cantidad"]


# ── Reportes ─────────────────────────────────────────────────────────────────

class ReporteReservas(BaseView):
    route_base = "/reportes/reservas"

    @expose("/")
    def index(self):
        reservas = Reserva.query.all()
        return self.render_template("reportes/reporte_reservas.html", reservas=reservas)


class ReportePagos(BaseView):
    route_base = "/reportes/pagos"

    @expose("/")
    def index(self):
        pagos = Pago.query.all()
        total = sum(p.monto for p in pagos)
        return self.render_template("reportes/reporte_pagos.html", pagos=pagos, total=total)


class ReporteServicios(BaseView):
    route_base = "/reportes/servicios"

    @expose("/")
    def index(self):
        items = ReservaServicio.query.all()
        total_servicios = sum(i.servicio.precio * i.cantidad for i in items)
        return self.render_template(
            "reportes/reporte_servicios.html",
            items=items,
            total_servicios=total_servicios,
        )


class ReporteGraficos(BaseView):
    route_base = "/reportes/graficos"

    @expose("/")
    def index(self):
        # Reservas agrupadas por estado
        reservas_estado = [
            {"estado": r.estado, "cantidad": c}
            for r, c in (
                db.session.query(Reserva, func.count(Reserva.id))
                .group_by(Reserva.estado).all()
            )
        ]

        # Habitaciones agrupadas por tipo
        habitaciones_tipo = [
            {"tipo": t.nombre, "cantidad": c}
            for t, c in (
                db.session.query(TipoHabitacion, func.count(Habitacion.id))
                .join(Habitacion, Habitacion.tipo_id == TipoHabitacion.id)
                .group_by(TipoHabitacion.nombre).all()
            )
        ]

        # Total recaudado por método de pago
        pagos_metodo = [
            {"metodo": metodo, "total": round(float(total), 2)}
            for metodo, total in (
                db.session.query(Pago.metodo, func.sum(Pago.monto))
                .group_by(Pago.metodo).all()
            )
        ]

        # Servicios más consumidos (suma de cantidades)
        servicios_consumo = [
            {"servicio": s.nombre, "total": int(total)}
            for s, total in (
                db.session.query(Servicio, func.sum(ReservaServicio.cantidad))
                .join(ReservaServicio, ReservaServicio.servicio_id == Servicio.id)
                .group_by(Servicio.nombre).all()
            )
        ]

        return self.render_template(
            "reportes/reporte_graficos.html",
            reservas_estado=reservas_estado,
            habitaciones_tipo=habitaciones_tipo,
            pagos_metodo=pagos_metodo,
            servicios_consumo=servicios_consumo,
        )


# ── Registro en el menú ──────────────────────────────────────────────────────
appbuilder.add_view(
    TipoHabitacionView, "Tipos de Habitación",
    icon="fa-bed", category="Habitaciones",
)
appbuilder.add_view(
    HabitacionView, "Habitaciones",
    icon="fa-home", category="Habitaciones",
)
appbuilder.add_view(
    ClienteView, "Clientes",
    icon="fa-user", category="Gestión",
)
appbuilder.add_view(
    ReservaView, "Reservas",
    icon="fa-calendar", category="Gestión",
)
appbuilder.add_view(
    PagoView, "Pagos",
    icon="fa-money", category="Gestión",
)
appbuilder.add_view(
    ServicioView, "Servicios",
    icon="fa-star", category="Catálogos",
)
appbuilder.add_view(
    ReservaServicioView, "Servicios por Reserva",
    icon="fa-list", category="Catálogos",
)
appbuilder.add_view_no_menu(ReporteReservas)
appbuilder.add_view_no_menu(ReportePagos)
appbuilder.add_view_no_menu(ReporteServicios)
appbuilder.add_view_no_menu(ReporteGraficos)

appbuilder.add_link(
    "Reservas Detalladas",
    href="/reportes/reservas/",
    icon="fa-calendar",
    category="Reportes",
)
appbuilder.add_link(
    "Pagos por Reserva",
    href="/reportes/pagos/",
    icon="fa-money",
    category="Reportes",
)
appbuilder.add_link(
    "Servicios Consumidos",
    href="/reportes/servicios/",
    icon="fa-star",
    category="Reportes",
)
appbuilder.add_link(
    "Gráficos",
    href="/reportes/graficos/",
    icon="fa-bar-chart",
    category="Reportes",
)
