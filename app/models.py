from .extensions import db
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
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
    reservas = relationship("Reserva", back_populates="habitacion")

    def __repr__(self):
        return f"Hab. {self.numero}"


class Cliente(db.Model):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    email = Column(String(150), unique=True)
    telefono = Column(String(20))

    reservas = relationship("Reserva", back_populates="cliente")

    def __repr__(self):
        return self.nombre


class Reserva(db.Model):
    __tablename__ = "reserva"

    id = Column(Integer, primary_key=True)
    fecha_entrada = Column(Date, nullable=False)
    fecha_salida = Column(Date, nullable=False)
    estado = Column(String(50), default="pendiente")
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    habitacion_id = Column(Integer, ForeignKey("habitacion.id"), nullable=False)

    cliente = relationship("Cliente", back_populates="reservas")
    habitacion = relationship("Habitacion", back_populates="reservas")
    pagos = relationship("Pago", back_populates="reserva")
    servicios = relationship("ReservaServicio", back_populates="reserva")

    def __repr__(self):
        return f"Reserva #{self.id}"


class Pago(db.Model):
    __tablename__ = "pago"

    id = Column(Integer, primary_key=True)
    monto = Column(Float, nullable=False)
    metodo = Column(String(50), nullable=False)
    fecha = Column(Date, nullable=False)
    reserva_id = Column(Integer, ForeignKey("reserva.id"), nullable=False)

    reserva = relationship("Reserva", back_populates="pagos")

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
