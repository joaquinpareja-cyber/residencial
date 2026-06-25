from flask_appbuilder import ModelView, BaseView, expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.fieldwidgets import Select2Widget
from flask_appbuilder.models.sqla.filters import FilterEqual
from wtforms import SelectField
from wtforms.validators import DataRequired
from sqlalchemy import func
from datetime import date

from .extensions import appbuilder, db
from .models import (
    TipoHabitacion, Habitacion, Cliente,
    Reserva, Pago, Servicio, ReservaServicio
)

# ── Opciones para los desplegables ───────────────────────────────────────────
ESTADO_CIVIL_CHOICES = [
    ("Soltero/a", "Soltero/a"),
    ("Casado/a", "Casado/a"),
    ("Divorciado/a", "Divorciado/a"),
    ("Viudo/a", "Viudo/a"),
    ("Unión Libre", "Unión Libre"),
]

ESTADO_RESERVA_CHOICES = [
    ("pendiente", "Pendiente"),
    ("confirmada", "Confirmada"),
    ("cancelada", "Cancelada"),
]

METODO_PAGO_CHOICES = [
    ("Efectivo", "Efectivo"),
    ("Tarjeta", "Tarjeta"),
    ("Transferencia", "Transferencia"),
    ("QR", "QR"),
]

ESTADO_HABITACION_CHOICES = [
    ("disponible", "Disponible"),
    ("ocupada", "Ocupada"),
    ("mantenimiento", "Mantenimiento"),
]


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

    add_form_extra_fields = {
        "estado": SelectField(
            "Estado",
            choices=ESTADO_HABITACION_CHOICES,
            widget=Select2Widget(),
        )
    }
    edit_form_extra_fields = add_form_extra_fields


class ClienteView(ModelView):
    datamodel = SQLAInterface(Cliente)
    label_columns = {
        "hora_ingreso": "Hora de Ingreso",
        "nombre_completo": "Nombre Completo",
        "procedencia": "Procedencia",
        "nacionalidad": "Nacionalidad",
        "profesion": "Profesión",
        "ci": "C.I.",
        "fecha_nacimiento": "Fecha de Nacimiento",
        "estado_civil": "Estado Civil",
        "email": "Correo Electrónico",
        "telefono": "Teléfono",
        "habitacion": "Habitación Asignada",
    }
    list_columns = [
        "hora_ingreso", "nombre_completo", "ci",
        "procedencia", "nacionalidad", "habitacion"
    ]
    add_columns  = [
        "hora_ingreso", "nombre_completo", "procedencia",
        "nacionalidad", "profesion", "ci", "fecha_nacimiento",
        "estado_civil", "email", "telefono", "habitacion",
    ]
    edit_columns = [
        "hora_ingreso", "nombre_completo", "procedencia",
        "nacionalidad", "profesion", "ci", "fecha_nacimiento",
        "estado_civil", "email", "telefono", "habitacion",
    ]
    show_columns = [
        "hora_ingreso", "nombre_completo", "procedencia",
        "nacionalidad", "profesion", "ci", "fecha_nacimiento",
        "estado_civil", "email", "telefono", "habitacion",
    ]

    add_form_extra_fields = {
        "estado_civil": SelectField(
            "Estado Civil",
            choices=ESTADO_CIVIL_CHOICES,
            widget=Select2Widget(),
        )
    }
    edit_form_extra_fields = add_form_extra_fields


class ReservaView(ModelView):
    datamodel = SQLAInterface(Reserva)
    label_columns = {
        "nombre_reservante": "Nombre del Reservante",
        "telefono_contacto": "Teléfono de Contacto",
        "habitacion": "Habitación",
        "fecha_entrada": "Fecha de Entrada",
        "fecha_salida": "Fecha de Salida",
        "estado": "Estado",
    }
    list_columns = [
        "nombre_reservante", "telefono_contacto",
        "habitacion", "fecha_entrada", "fecha_salida", "estado"
    ]
    add_columns  = [
        "nombre_reservante", "telefono_contacto",
        "habitacion", "fecha_entrada", "fecha_salida", "estado"
    ]
    edit_columns = [
        "nombre_reservante", "telefono_contacto",
        "habitacion", "fecha_entrada", "fecha_salida", "estado"
    ]
    show_columns = [
        "nombre_reservante", "telefono_contacto",
        "habitacion", "fecha_entrada", "fecha_salida", "estado"
    ]

    add_form_extra_fields = {
        "estado": SelectField(
            "Estado",
            choices=ESTADO_RESERVA_CHOICES,
            widget=Select2Widget(),
        )
    }
    edit_form_extra_fields = add_form_extra_fields


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

    add_form_extra_fields = {
        "metodo": SelectField(
            "Método de Pago",
            choices=METODO_PAGO_CHOICES,
            widget=Select2Widget(),
        )
    }
    edit_form_extra_fields = add_form_extra_fields


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


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardView(BaseView):
    route_base = "/dashboard"
    default_view = "index"

    @expose("/")
    def index(self):
        hoy = date.today()

        total_clientes = Cliente.query.count()
        clientes_hoy = Cliente.query.count()

        total_habitaciones = Habitacion.query.count()
        hab_disponibles = Habitacion.query.filter_by(estado="disponible").count()
        hab_ocupadas = Habitacion.query.filter_by(estado="ocupada").count()
        hab_mantenimiento = Habitacion.query.filter_by(estado="mantenimiento").count()
        habitaciones = Habitacion.query.all()

        total_reservas = Reserva.query.count()
        reservas_pendientes = Reserva.query.filter_by(estado="pendiente").count()
        ultimas_reservas = Reserva.query.order_by(Reserva.id.desc()).limit(5).all()

        recaudado_total = db.session.query(func.sum(Pago.monto)).scalar() or 0
        recaudado_mes = db.session.query(func.sum(Pago.monto)).filter(
            func.month(Pago.fecha) == hoy.month,
            func.year(Pago.fecha) == hoy.year
        ).scalar() or 0

        ultimos_clientes = Cliente.query.order_by(Cliente.id.desc()).limit(5).all()

        return self.render_template(
            "dashboard.html",
            total_clientes=total_clientes,
            clientes_hoy=clientes_hoy,
            total_habitaciones=total_habitaciones,
            hab_disponibles=hab_disponibles,
            hab_ocupadas=hab_ocupadas,
            hab_mantenimiento=hab_mantenimiento,
            habitaciones=habitaciones,
            total_reservas=total_reservas,
            reservas_pendientes=reservas_pendientes,
            ultimas_reservas=ultimas_reservas,
            recaudado_total=recaudado_total,
            recaudado_mes=recaudado_mes,
            ultimos_clientes=ultimos_clientes,
        )


# ── Vista visual de habitaciones ─────────────────────────────────────────────

class HabitacionesVisualView(BaseView):
    route_base = "/habitaciones/visual"

    @expose("/")
    def index(self):
        habitaciones = Habitacion.query.order_by(Habitacion.numero).all()

        # Agrupar por tipo
        habitaciones_por_tipo = {}
        for h in habitaciones:
            tipo = h.tipo.nombre
            if tipo not in habitaciones_por_tipo:
                habitaciones_por_tipo[tipo] = []
            habitaciones_por_tipo[tipo].append(h)

        disponibles   = sum(1 for h in habitaciones if h.estado == "disponible")
        ocupadas      = sum(1 for h in habitaciones if h.estado == "ocupada")
        mantenimiento = sum(1 for h in habitaciones if h.estado == "mantenimiento")

        return self.render_template(
            "habitaciones_visual.html",
            habitaciones_por_tipo=habitaciones_por_tipo,
            disponibles=disponibles,
            ocupadas=ocupadas,
            mantenimiento=mantenimiento,
        )


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
        reservas_estado = [
            {"estado": estado, "cantidad": c}
            for estado, c in (
                db.session.query(Reserva.estado, func.count(Reserva.id))
                .group_by(Reserva.estado).all()
            )
        ]
        habitaciones_tipo = [
            {"tipo": t.nombre, "cantidad": c}
            for t, c in (
                db.session.query(TipoHabitacion, func.count(Habitacion.id))
                .join(Habitacion, Habitacion.tipo_id == TipoHabitacion.id)
                .group_by(TipoHabitacion.nombre).all()
            )
        ]
        pagos_metodo = [
            {"metodo": metodo, "total": round(float(total), 2)}
            for metodo, total in (
                db.session.query(Pago.metodo, func.sum(Pago.monto))
                .group_by(Pago.metodo).all()
            )
        ]
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
    DashboardView, "Inicio",
    icon="fa-dashboard", category="",
)
appbuilder.add_view(
    TipoHabitacionView, "Tipos de Habitación",
    icon="fa-bed", category="Habitaciones",
)
appbuilder.add_view(
    HabitacionView, "Habitaciones",
    icon="fa-home", category="Habitaciones",
)
appbuilder.add_view_no_menu(HabitacionesVisualView)
appbuilder.add_link(
    "Vista Visual",
    href="/habitaciones/visual/",
    icon="fa-th-large",
    category="Habitaciones",
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
