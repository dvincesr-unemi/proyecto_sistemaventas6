from datetime import date


# =====================================================================
# CLASE BASE: lo que los modelos comparten
# =====================================================================
class ModeloBase:
    """Padre de todos los modelos. Guarda el id y define el comportamiento común."""

    def __init__(self, id_registro):
        self.id = int(id_registro)

    # ---- ÚNICO MÉTODO DE CLASE DEL PROYECTO ----
    @classmethod
    def desde_diccionario(cls, datos):
        """Diccionario -> objeto. Escrito UNA vez y usado por todos los modelos.
        cls es la clase que llamó: Cliente, Proveedor, Producto o Venta."""
        datos = dict(datos)                 # copia, para no tocar el original
        id_registro = datos.pop("id")       # saco el id
        return cls(id_registro, **datos)    # el resto son los campos del modelo

    # ---- MÉTODOS DE INSTANCIA ----
    def a_diccionario(self):
        # Objeto -> diccionario. Cada hijo agrega sus campos.
        return {"id": self.id}

    def etiqueta(self):
        # POLIMORFISMO: cada hijo la reescribe a su manera
        return f"registro {self.id}"

    def __str__(self):
        # Lo que se ve al hacer print(objeto). Llama a etiqueta(),
        # así que cada modelo se imprime distinto sin cambiar esta línea.
        return f"[{self.id}] {self.etiqueta()}"


# =====================================================================
# HERENCIA: Persona es la base de Cliente y Proveedor
# =====================================================================
class Persona(ModeloBase):
    """Todo lo que tiene una persona del sistema."""

    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)      # el padre guarda el id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self):
        datos = super().a_diccionario()    # {"id": ...} que arma el padre
        datos["nombre"] = self.nombre
        datos["apellido"] = self.apellido
        datos["email"] = self.email
        return datos

    def etiqueta(self):
        return self.nombre_completo()


class Cliente(Persona):
    """Cliente ES UNA Persona, con teléfono y ciudad."""

    def __init__(self, id_registro, nombre, apellido, email, telefono="", ciudad=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.telefono = telefono
        self.ciudad = ciudad

    def a_diccionario(self):
        datos = super().a_diccionario()    # reutiliza lo de Persona
        datos["telefono"] = self.telefono
        datos["ciudad"] = self.ciudad
        return datos

    def etiqueta(self):
        # Sobrescribe y EXTIENDE la del padre
        return f"{super().etiqueta()} · {self.email} · {self.ciudad or 'sin ciudad'}"


# =====================================================================
# PROVEEDOR: Hereda de Persona (contacto y empresa proveedora)
# =====================================================================
class Proveedor(Persona):
    """Proveedor ES UNA Persona (contacto), asociada a una empresa o marca comercial."""

    def __init__(self, id_registro, nombre, apellido, email, empresa="", telefono=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.empresa = empresa
        self.telefono = telefono

    def a_diccionario(self):
        datos = super().a_diccionario()    # reutiliza id, nombre, apellido, email
        datos["empresa"] = self.empresa
        datos["telefono"] = self.telefono
        return datos

    def etiqueta(self):
        empresa_info = f"[{self.empresa}] " if self.empresa else ""
        return f"{empresa_info}{super().etiqueta()} · {self.email} · {self.telefono or 'sin teléfono'}"


# =====================================================================
# PRODUCTO: Enlazado al Proveedor mediante proveedor_id
# =====================================================================
class Producto(ModeloBase):
    """Producto ES UN ModeloBase. Asociado al proveedor que suministra el stock."""

    # ATRIBUTOS ESTÁTICOS (de clase): existen una sola vez, no por objeto
    STOCK_MINIMO = 5          # regla del negocio, igual para todos los productos
    IVA = 0.15                # 15 %
    total_creados = 0         # contador compartido

    def __init__(self, id_registro, nombre, precio, stock=0, proveedor_id=0):
        super().__init__(id_registro)
        self.nombre = nombre
        self.precio = float(precio)
        self.stock = int(stock)
        self.proveedor_id = int(proveedor_id)  # Referencia al Proveedor
        Producto.total_creados += 1            # se modifica en la CLASE, no en self

    # MÉTODOS ESTÁTICOS: reglas que no necesitan ningún producto concreto
    @staticmethod
    def es_precio_valido(valor):
        try:
            return float(valor) > 0
        except (TypeError, ValueError):
            return False

    @staticmethod
    def con_iva(monto):
        return round(monto * (1 + Producto.IVA), 2)

    # MÉTODOS DE INSTANCIA: necesitan los datos de ESTE producto
    def stock_bajo(self):
        return self.stock <= Producto.STOCK_MINIMO

    def hay_stock(self, cantidad):
        return 0 < cantidad <= self.stock

    def descontar_stock(self, cantidad):
        self.stock -= cantidad

    def devolver_stock(self, cantidad):
        self.stock += cantidad

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["precio"] = self.precio
        datos["stock"] = self.stock
        datos["proveedor_id"] = self.proveedor_id
        return datos

    def etiqueta(self):
        alerta = " ⚠ stock bajo" if self.stock_bajo() else ""
        prov_info = f" · Prov: {self.proveedor_id}" if self.proveedor_id else ""
        return f"{self.nombre}{prov_info} · ${self.precio:.2f} · stock {self.stock}{alerta}"


# =====================================================================
# VENTA: Flujo 1 a 1 intacto
# =====================================================================
class Venta(ModeloBase):
    """Venta simple: un cliente, un producto, una cantidad."""

    def __init__(self, id_registro, cliente_id, producto_id, cantidad,
                 precio_unitario, fecha=""):
        super().__init__(id_registro)
        self.cliente_id = int(cliente_id)
        self.producto_id = int(producto_id)
        self.cantidad = int(cantidad)
        self.precio_unitario = float(precio_unitario)
        self.fecha = fecha or date.today().isoformat()

    def calcular_total(self):
        return round(self.cantidad * self.precio_unitario, 2)

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["cliente_id"] = self.cliente_id
        datos["producto_id"] = self.producto_id
        datos["cantidad"] = self.cantidad
        datos["precio_unitario"] = self.precio_unitario
        datos["fecha"] = self.fecha
        return datos

    def etiqueta(self):
        return (f"{self.fecha} · cliente {self.cliente_id} · "
                f"{self.cantidad} x producto {self.producto_id} "
                f"= ${self.calcular_total():.2f}")