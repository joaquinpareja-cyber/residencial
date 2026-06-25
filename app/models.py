from .extensions import db
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship


class TipoHabitacion(db.Model):
    __tablename__ = "tipo_habitacion"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    capacidad = Column(Integer, nullable=False)
    descripcion = Column(String(255))

    habitaciones = relationship("Habitacion", back_populates="tipo")

    def __repr__(self):
        return self.nombre


class Habitacion(db.Model):
    __tablename__ = "habitacion"

    id = Column(Integer, primary_key=True)
    numero = Column(String(10), nullable=False, unique=True)
    precio_noche = Column(Float, nullable=False)
    estado = Column(String(50), default="disponible")
    tipo_id = Column(Integer, ForeignKey("tipo_habitacion.id"), nullable=False)

    tipo = relationship("TipoHabitacion", back_populates="habitaciones")
    clientes = relationship("Cliente", back_populates="habitacion")
    reservas = relationship("Reserva", back_populates="habitacion")

    def __repr__(self):
        return f"Hab. {self.numero}"


class Cliente(db.Model):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True)
    nombre_completo = Column(String(200), nullable=False)
    ci = Column(String(20), nullable=False, unique=True)
    fecha_nacimiento = Column(Date)
    nacionalidad = Column(String(100))
    procedencia = Column(String(150))
    profesion = Column(String(100))
    estado_civil = Column(String(50))
    email = Column(String(150))
    telefono = Column(String(20))
    hora_ingreso = Column(String(10))
    activo = Column(Boolean, default=True)
    monto_pago = Column(Float, nullable=True)
    metodo_pago = Column(String(50), nullable=True)
    habitacion_id = Column(Integer, ForeignKey("habitacion.id"), nullable=True)

    habitacion = relationship("Habitacion", back_populates="clientes")
    pagos = relationship("Pago", back_populates="cliente")

    def __repr__(self):
        return self.nombre_completo


class Reserva(db.Model):
    __tablename__ = "reserva"

    id = Column(Integer, primary_key=True)
    nombre_reservante = Column(String(200), nullable=False)
    telefono_contacto = Column(String(20))
    fecha_entrada = Column(Date, nullable=False)
    fecha_salida = Column(Date, nullable=False)
    estado = Column(String(50), default="pendiente")
    habitacion_id = Column(Integer, ForeignKey("habitacion.id"), nullable=False)

    habitacion = relationship("Habitacion", back_populates="reservas")
    pagos = relationship("Pago", back_populates="reserva")
    servicios = relationship("ReservaServicio", back_populates="reserva")

    def __repr__(self):
        return f"Reserva #{self.id} - {self.nombre_reservante}"


class Pago(db.Model):
    __tablename__ = "pago"

    id = Column(Integer, primary_key=True)
    monto = Column(Float, nullable=False)
    metodo = Column(String(50), nullable=False)
    fecha = Column(Date, nullable=False)
    reserva_id = Column(Integer, ForeignKey("reserva.id"), nullable=True)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=True)

    reserva = relationship("Reserva", back_populates="pagos")
    cliente = relationship("Cliente", back_populates="pagos")

    def __repr__(self):
        return f"Pago #{self.id} - Bs {self.monto}"


class Servicio(db.Model):
    __tablename__ = "servicio"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    precio = Column(Float, nullable=False)

    reservas = relationship("ReservaServicio", back_populates="servicio")

    def __repr__(self):
        return self.nombre


class ReservaServicio(db.Model):
    __tablename__ = "reserva_servicio"

    id = Column(Integer, primary_key=True)
    cantidad = Column(Integer, default=1, nullable=False)
    reserva_id = Column(Integer, ForeignKey("reserva.id"), nullable=False)
    servicio_id = Column(Integer, ForeignKey("servicio.id"), nullable=False)

    reserva = relationship("Reserva", back_populates="servicios")
    servicio = relationship("Servicio", back_populates="reservas")

    def __repr__(self):
        return f"{self.servicio} x{self.cantidad}"
