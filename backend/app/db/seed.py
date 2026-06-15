from sqlalchemy import text
from sqlmodel import Session, select

from app.core.db import engine
from app.core.security import hash_password
from app.models.estado_pedido import EstadoPedido
from app.models.forma_pago import FormaPago
from app.models.rol import Rol
from app.models.unidad_medida import UnidadMedida
from app.models.usuario import Usuario

ROLES = [
    ("ADMIN", "Administrador", "CRUD completo de todo el sistema"),
    ("STOCK", "Gestor de Stock", "Leer productos, actualizar stock y disponibilidad"),
    ("PEDIDOS", "Gestor de Pedidos", "Ver y avanzar estados de pedidos"),
    ("CLIENT", "Cliente", "Catálogo, carrito y pedidos propios"),
]

# ERD v7 / TPI v6: máquina de estados de 5 estados. EN_CAMINO queda eliminado.
ESTADOS_PEDIDO = [
    ("PENDIENTE", "Pendiente", 1, True, False),
    ("CONFIRMADO", "Confirmado", 2, True, False),
    ("EN_PREP", "En preparación", 3, False, False),
    ("ENTREGADO", "Entregado", 4, False, True),
    ("CANCELADO", "Cancelado", 5, False, True),
]

ESTADOS_OBSOLETOS = {"EN_PREPARACION", "EN_CAMINO"}

FORMAS_PAGO = [
    ("MERCADOPAGO", "MercadoPago", "Pago online mediante MercadoPago Checkout Pro"),
    ("EFECTIVO", "Efectivo", "Pago en efectivo al recibir el pedido"),
    ("TRANSFERENCIA", "Transferencia", "Pago por transferencia bancaria"),
]

FORMAS_PAGO_OBSOLETAS = {"MERCADO_PAGO"}

UNIDADES_MEDIDA = [
    ("Unidad", "ud", "contable"),
    ("Kilogramo", "kg", "peso"),
    ("Gramo", "g", "peso"),
    ("Litro", "L", "volumen"),
    ("Mililitro", "ml", "volumen"),
]

ADMIN_EMAIL = "admin@parcial.com"
ADMIN_PASSWORD = "Admin1234"



def _ensure_v7_schema(session: Session) -> None:
    """Agrega columnas v7 cuando se reutiliza una BD ya creada con create_all().

    create_all() crea tablas nuevas, pero no modifica tablas existentes.
    Estas instrucciones hacen segura la actualización local sin borrar datos.
    """
    statements = [
        "ALTER TABLE IF EXISTS producto ADD COLUMN IF NOT EXISTS unidad_venta_id BIGINT",
        "ALTER TABLE IF EXISTS ingrediente ADD COLUMN IF NOT EXISTS stock_cantidad NUMERIC(12,3) NOT NULL DEFAULT 0",
        "ALTER TABLE IF EXISTS ingrediente ALTER COLUMN stock_cantidad TYPE NUMERIC(12,3) USING stock_cantidad::numeric",
        "ALTER TABLE IF EXISTS ingrediente ADD COLUMN IF NOT EXISTS unidad_medida_id BIGINT",
        "ALTER TABLE IF EXISTS producto_ingrediente ADD COLUMN IF NOT EXISTS cantidad NUMERIC(10,3) NOT NULL DEFAULT 1",
        "ALTER TABLE IF EXISTS producto_ingrediente ADD COLUMN IF NOT EXISTS unidad_medida_id BIGINT",
        "ALTER TABLE IF EXISTS producto ADD COLUMN IF NOT EXISTS stock_cantidad INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE IF EXISTS usuario ADD COLUMN IF NOT EXISTS celular VARCHAR(20)",
        "ALTER TABLE IF EXISTS usuario_rol ADD COLUMN IF NOT EXISTS asignado_por_id BIGINT",
        "ALTER TABLE IF EXISTS usuario_rol ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ",
        "ALTER TABLE IF EXISTS pago ADD COLUMN IF NOT EXISTS transaction_amount NUMERIC(10,2) NOT NULL DEFAULT 0",
        "ALTER TABLE IF EXISTS pago ADD COLUMN IF NOT EXISTS payment_method_id VARCHAR(50)",
        "ALTER TABLE IF EXISTS pago ADD COLUMN IF NOT EXISTS external_reference VARCHAR(100)",
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'producto_unidad_venta_id_fkey') THEN
                ALTER TABLE producto ADD CONSTRAINT producto_unidad_venta_id_fkey
                FOREIGN KEY (unidad_venta_id) REFERENCES unidad_medida(id);
            END IF;
        END $$;
        """,
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'producto_ingrediente_unidad_medida_id_fkey') THEN
                ALTER TABLE producto_ingrediente ADD CONSTRAINT producto_ingrediente_unidad_medida_id_fkey
                FOREIGN KEY (unidad_medida_id) REFERENCES unidad_medida(id);
            END IF;
        END $$;
        """,
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ingrediente_unidad_medida_id_fkey') THEN
                ALTER TABLE ingrediente ADD CONSTRAINT ingrediente_unidad_medida_id_fkey
                FOREIGN KEY (unidad_medida_id) REFERENCES unidad_medida(id);
            END IF;
        END $$;
        """,
    ]

    for statement in statements:
        session.exec(text(statement))
    session.commit()



def _migrar_en_preparacion_a_en_prep(session: Session) -> None:
    """Migra bases existentes al código literal del TPI v6/ERD v7.

    Versiones anteriores del integrador usaban EN_PREPARACION. El PDF define
    EN_PREP como código oficial de la FSM, por eso se actualizan pedidos e
    historial antes de marcar el estado viejo como obsoleto.
    """
    statements = [
        "UPDATE pedido SET estado_codigo = 'EN_PREP' WHERE estado_codigo = 'EN_PREPARACION'",
        "UPDATE historial_estado_pedido SET estado_desde = 'EN_PREP' WHERE estado_desde = 'EN_PREPARACION'",
        "UPDATE historial_estado_pedido SET estado_hacia = 'EN_PREP' WHERE estado_hacia = 'EN_PREPARACION'",
    ]
    for statement in statements:
        session.exec(text(statement))


def run_seed() -> None:
    with Session(engine) as session:
        _ensure_v7_schema(session)
        roles_por_codigo: dict[str, Rol] = {}

        for codigo, nombre, descripcion in ROLES:
            rol = session.exec(select(Rol).where(Rol.codigo == codigo)).first()
            if rol is None:
                rol = Rol(codigo=codigo, nombre=nombre, descripcion=descripcion)
                session.add(rol)
                session.flush()
            else:
                rol.nombre = nombre
                rol.descripcion = descripcion
                rol.activo = True
                session.add(rol)
            roles_por_codigo[codigo] = rol

        for codigo, nombre, orden, permite_cancelacion, es_final in ESTADOS_PEDIDO:
            estado = session.exec(select(EstadoPedido).where(EstadoPedido.codigo == codigo)).first()
            if estado is None:
                estado = EstadoPedido(codigo=codigo)
            estado.nombre = nombre
            estado.orden = orden
            estado.permite_cancelacion_cliente = permite_cancelacion
            estado.es_final = es_final
            estado.activo = True
            estado.deleted_at = None
            session.add(estado)

        session.flush()
        _migrar_en_preparacion_a_en_prep(session)

        for codigo in ESTADOS_OBSOLETOS:
            estado = session.exec(select(EstadoPedido).where(EstadoPedido.codigo == codigo)).first()
            if estado is not None:
                estado.activo = False
                session.add(estado)

        for codigo, nombre, descripcion in FORMAS_PAGO:
            forma_pago = session.exec(select(FormaPago).where(FormaPago.codigo == codigo)).first()
            if forma_pago is None:
                forma_pago = FormaPago(codigo=codigo)
            forma_pago.nombre = nombre
            forma_pago.descripcion = descripcion
            forma_pago.activo = True
            forma_pago.deleted_at = None
            session.add(forma_pago)

        for codigo in FORMAS_PAGO_OBSOLETAS:
            forma_pago = session.exec(select(FormaPago).where(FormaPago.codigo == codigo)).first()
            if forma_pago is not None:
                forma_pago.activo = False
                session.add(forma_pago)

        for nombre, simbolo, tipo in UNIDADES_MEDIDA:
            unidad = session.exec(select(UnidadMedida).where(UnidadMedida.simbolo == simbolo)).first()
            if unidad is None:
                unidad = UnidadMedida(nombre=nombre, simbolo=simbolo, tipo=tipo)
            else:
                unidad.nombre = nombre
                unidad.tipo = tipo
            unidad.activo = True
            unidad.deleted_at = None
            session.add(unidad)

        admin = session.exec(select(Usuario).where(Usuario.email == ADMIN_EMAIL)).first()
        if admin is None:
            admin = Usuario(
                email=ADMIN_EMAIL,
                nombre="Admin",
                apellido="Parcial",
                password_hash=hash_password(ADMIN_PASSWORD),
            )
            admin.roles = [roles_por_codigo["ADMIN"]]
            session.add(admin)

        session.commit()


if __name__ == "__main__":
    run_seed()
    print("Seed obligatorio ejecutado correctamente.")
    print(f"Usuario admin: {ADMIN_EMAIL}")
    print(f"Contraseña admin: {ADMIN_PASSWORD}")
