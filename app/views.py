from flask_appbuilder import ModelView, BaseView, expose
from flask import redirect, url_for
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.fieldwidgets import Select2Widget
from flask_appbuilder.models.sqla.filters import FilterEqual
from wtforms import SelectField, FloatField
from wtforms.validators import DataRequired
from sqlalchemy import func
from datetime import date, datetime

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


def reservas_en_conflicto(habitacion_id, fecha_entrada, fecha_salida, exclude_reserva_id=None):
    """Reservas activas que solapan con el rango [entrada, salida)."""
    if not habitacion_id or not fecha_entrada or not fecha_salida:
        return []
    if fecha_salida <= fecha_entrada:
        return []

    q = db.session.query(Reserva).filter(
        Reserva.habitacion_id == habitacion_id,
        Reserva.estado != "cancelada",
        Reserva.fecha_entrada < fecha_salida,
        Reserva.fecha_salida > fecha_entrada,
    )
    if exclude_reserva_id:
        q = q.filter(Reserva.id != exclude_reserva_id)
    return q.all()


def mensaje_conflicto_reserva(conflictos):
    detalle = "; ".join(
        f"#{r.id} {r.nombre_reservante} "
        f"({r.fecha_entrada.strftime('%d/%m/%Y')} - {r.fecha_salida.strftime('%d/%m/%Y')})"
        for r in conflictos
    )
    return f"La habitación ya está ocupada en esas fechas: {detalle}"


def sincronizar_estados_habitaciones():
    habitaciones = Habitacion.query.all()
    cambios = False

    for habitacion in habitaciones:
        if habitacion.estado == "mantenimiento":
            continue

        tiene_cliente_activo = (
            Cliente.query.filter(
                Cliente.habitacion_id == habitacion.id,
                Cliente.activo.is_(True),
            ).first() is not None
        )
        nuevo_estado = "ocupada" if tiene_cliente_activo else "disponible"
        if habitacion.estado != nuevo_estado:
            habitacion.estado = nuevo_estado
            cambios = True

    if cambios:
        db.session.commit()


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
        "monto_pago": "Monto del Pago (Bs)",
        "metodo_pago": "Método de Pago",
    }
    list_columns = [
        "hora_ingreso", "nombre_completo", "ci",
        "procedencia", "nacionalidad", "habitacion", "activo",
        "monto_pago", "metodo_pago"
    ]
    add_columns  = [
        "hora_ingreso", "nombre_completo", "procedencia",
        "nacionalidad", "profesion", "ci", "fecha_nacimiento",
        "estado_civil", "email", "telefono", "habitacion",
        "monto_pago", "metodo_pago",
    ]
    edit_columns = [
        "hora_ingreso", "nombre_completo", "procedencia",
        "nacionalidad", "profesion", "ci", "fecha_nacimiento",
        "estado_civil", "email", "telefono", "habitacion",
        "monto_pago", "metodo_pago",
    ]
    show_columns = [
        "hora_ingreso", "nombre_completo", "procedencia",
        "nacionalidad", "profesion", "ci", "fecha_nacimiento",
        "estado_civil", "email", "telefono", "habitacion", "activo",
        "monto_pago", "metodo_pago",
    ]

    add_form_extra_fields = {
        "estado_civil": SelectField(
            "Estado Civil",
            choices=ESTADO_CIVIL_CHOICES,
            widget=Select2Widget(),
        ),
        "metodo_pago": SelectField(
            "Método de Pago",
            choices=METODO_PAGO_CHOICES,
            widget=Select2Widget(),
        ),
        "monto_pago": FloatField("Monto del Pago (Bs)"),
    }
    edit_form_extra_fields = add_form_extra_fields

    def _hay_otros_clientes_en_habitacion(self, habitacion_id, exclude_cliente_id=None):
        query = Cliente.query.filter(Cliente.habitacion_id == habitacion_id)
        if exclude_cliente_id is not None:
            query = query.filter(Cliente.id != exclude_cliente_id)
        return query.first() is not None

    def _obtener_habitacion_id(self, item):
        if getattr(item, "habitacion_id", None):
            return item.habitacion_id
        habitacion = getattr(item, "habitacion", None)
        if habitacion is not None:
            return getattr(habitacion, "id", None)
        return None

    def _actualizar_estado_habitacion(self, item, old_habitacion_id=None):
        habitacion_id = self._obtener_habitacion_id(item)

        if old_habitacion_id and old_habitacion_id != habitacion_id:
            habitacion_anterior = db.session.get(Habitacion, old_habitacion_id)
            if habitacion_anterior and not self._hay_otros_clientes_en_habitacion(old_habitacion_id, exclude_cliente_id=item.id):
                habitacion_anterior.estado = "disponible"

        if habitacion_id:
            habitacion = db.session.get(Habitacion, habitacion_id)
            if habitacion:
                habitacion.estado = "ocupada"

    def _guardar_pago_cliente(self, item):
        if not item:
            return

        monto_raw = getattr(item, "monto_pago", None)
        metodo = getattr(item, "metodo_pago", None)
        if monto_raw in (None, ""):
            return

        try:
            monto = float(monto_raw)
        except (TypeError, ValueError):
            return

        if monto <= 0 or not metodo:
            return

        if item not in db.session:
            db.session.add(item)

        if getattr(item, "id", None) is None:
            db.session.flush()

        pago_existente = None
        if getattr(item, "id", None):
            pago_existente = db.session.query(Pago).filter(Pago.cliente_id == item.id).first()

        if pago_existente is not None:
            pago_existente.monto = monto
            pago_existente.metodo = metodo
            pago_existente.fecha = date.today()
        else:
            pago = Pago(
                monto=monto,
                metodo=metodo,
                fecha=date.today(),
                cliente_id=item.id,
                reserva_id=None,
            )
            db.session.add(pago)

    def pre_add(self, item):
        self._actualizar_estado_habitacion(item)
        self._guardar_pago_cliente(item)

    def post_add(self, item):
        db.session.commit()

    def pre_update(self, item):
        cliente_actual = db.session.get(Cliente, item.id)
        old_habitacion_id = cliente_actual.habitacion_id if cliente_actual else None
        self._actualizar_estado_habitacion(item, old_habitacion_id=old_habitacion_id)
        self._guardar_pago_cliente(item)

    def post_update(self, item):
        db.session.commit()

    def pre_delete(self, item):
        if item.habitacion_id:
            habitacion = db.session.get(Habitacion, item.habitacion_id)
            if habitacion and not self._hay_otros_clientes_en_habitacion(item.habitacion_id, exclude_cliente_id=item.id):
                habitacion.estado = "disponible"
        sincronizar_estados_habitaciones()

    @expose("/check_out/<int:cliente_id>")
    def check_out(self, cliente_id):
        cliente = db.session.get(Cliente, cliente_id)
        if cliente:
            if cliente.habitacion_id:
                habitacion = db.session.get(Habitacion, cliente.habitacion_id)
                if habitacion and not self._hay_otros_clientes_en_habitacion(cliente.habitacion_id, exclude_cliente_id=cliente.id):
                    habitacion.estado = "disponible"
                cliente.habitacion_id = None
            cliente.activo = False
            db.session.commit()
            sincronizar_estados_habitaciones()
        return redirect(url_for("ClienteView.list"))

    def get_list_widget(self, *args, **kwargs):
        widget = super().get_list_widget(*args, **kwargs)
        return widget


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

    add_template  = "reserva_form_add.html"
    edit_template = "reserva_form.html"

    def _validar_disponibilidad(self, item, exclude_reserva_id=None):
        if item.fecha_salida <= item.fecha_entrada:
            raise Exception("La fecha de salida debe ser posterior a la fecha de entrada.")

        conflictos = reservas_en_conflicto(
            item.habitacion_id,
            item.fecha_entrada,
            item.fecha_salida,
            exclude_reserva_id=exclude_reserva_id,
        )
        if conflictos:
            raise Exception(mensaje_conflicto_reserva(conflictos))

    def pre_add(self, item):
        self._validar_disponibilidad(item)

    def pre_update(self, item):
        self._validar_disponibilidad(item, exclude_reserva_id=item.id)


class PagoView(ModelView):
    datamodel = SQLAInterface(Pago)
    label_columns = {
        "reserva": "Reserva",
        "cliente": "Cliente",
        "monto": "Monto (Bs)",
        "metodo": "Método de pago",
        "fecha": "Fecha",
    }
    list_columns = ["reserva", "cliente", "monto", "metodo", "fecha"]
    add_columns  = ["reserva", "cliente", "monto", "metodo", "fecha"]
    edit_columns = ["reserva", "cliente", "monto", "metodo", "fecha"]
    show_columns = ["reserva", "cliente", "monto", "metodo", "fecha"]

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


# ── API de precios ───────────────────────────────────────────────────────────

from flask import jsonify, request

class HabitacionesPreciosAPI(BaseView):
    route_base = "/api/habitaciones_precios"

    @expose("/")
    def index(self):
        habitaciones = Habitacion.query.all()
        data = {
            str(h.id): {
                "numero": h.numero,
                "tipo": h.tipo.nombre,
                "precio": h.precio_noche,
            }
            for h in habitaciones
        }
        return jsonify(data)


class ReservaDisponibilidadAPI(BaseView):
    route_base = "/api/reserva_disponibilidad"

    @expose("/")
    def index(self):
        habitacion_id = request.args.get("habitacion_id", type=int)
        fecha_entrada = request.args.get("fecha_entrada")
        fecha_salida = request.args.get("fecha_salida")
        exclude_id = request.args.get("exclude_id", type=int)

        if not habitacion_id or not fecha_entrada or not fecha_salida:
            return jsonify({"disponible": True, "conflictos": []})

        try:
            entrada = datetime.strptime(fecha_entrada, "%Y-%m-%d").date()
            salida = datetime.strptime(fecha_salida, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"disponible": True, "conflictos": [], "error": "Fechas inválidas"})

        if salida <= entrada:
            return jsonify({
                "disponible": False,
                "conflictos": [],
                "error": "La fecha de salida debe ser posterior a la de entrada.",
            })

        conflictos = reservas_en_conflicto(habitacion_id, entrada, salida, exclude_id)
        return jsonify({
            "disponible": len(conflictos) == 0,
            "conflictos": [
                {
                    "id": r.id,
                    "nombre_reservante": r.nombre_reservante,
                    "fecha_entrada": r.fecha_entrada.isoformat(),
                    "fecha_salida": r.fecha_salida.isoformat(),
                    "estado": r.estado,
                }
                for r in conflictos
            ],
        })


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardView(BaseView):
    route_base = "/dashboard"
    default_view = "index"

    @expose("/")
    def index(self):
        sincronizar_estados_habitaciones()
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

class SincronizarHabitacionesView(BaseView):
    route_base = "/habitaciones/sincronizar"

    @expose("/")
    def index(self):
        sincronizar_estados_habitaciones()
        return redirect(url_for("HabitacionesVisualView.index"))


class HabitacionesVisualView(BaseView):
    route_base = "/habitaciones/visual"

    @expose("/")
    def index(self):
        sincronizar_estados_habitaciones()
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

class ReporteClientes(BaseView):
    route_base = "/reportes/clientes"

    @expose("/")
    def index(self):
        clientes = Cliente.query.all()
        return self.render_template("reportes/reporte_clientes.html", clientes=clientes)


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
        pagos = (
            Pago.query.order_by(Pago.fecha.desc(), Pago.id.desc()).all()
        )
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
        reservas_por_habitacion = [
            {"habitacion": f"Hab. {numero}", "cantidad": int(cantidad)}
            for numero, cantidad in (
                db.session.query(Habitacion.numero, func.count(Reserva.id))
                .join(Reserva, Reserva.habitacion_id == Habitacion.id)
                .group_by(Habitacion.numero)
                .all()
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
            reservas_por_habitacion=reservas_por_habitacion,
            servicios_consumo=servicios_consumo,
        )


# ── Registro en el menú ──────────────────────────────────────────────────────
appbuilder.add_view_no_menu(HabitacionesPreciosAPI)
appbuilder.add_view_no_menu(ReservaDisponibilidadAPI)
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
appbuilder.add_view_no_menu(SincronizarHabitacionesView)
appbuilder.add_link(
    "Vista Visual",
    href="/habitaciones/visual/",
    icon="fa-th-large",
    category="Habitaciones",
)
appbuilder.add_link(
    "Sincronizar Estados",
    href="/habitaciones/sincronizar/",
    icon="fa-refresh",
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
appbuilder.add_view_no_menu(ReporteClientes)
appbuilder.add_view_no_menu(ReporteReservas)
appbuilder.add_view_no_menu(ReportePagos)
appbuilder.add_view_no_menu(ReporteGraficos)

appbuilder.add_link(
    "Clientes",
    href="/reportes/clientes/",
    icon="fa-users",
    category="Reportes",
)
appbuilder.add_link(
    "Reservas",
    href="/reportes/reservas/",
    icon="fa-calendar",
    category="Reportes",
)
appbuilder.add_link(
    "Pagos",
    href="/reportes/pagos/",
    icon="fa-money",
    category="Reportes",
)
appbuilder.add_link(
    "Gráficos",
    href="/reportes/graficos/",
    icon="fa-bar-chart",
    category="Reportes",
)

# Exportaciones
from .exports import register_exports
register_exports()
