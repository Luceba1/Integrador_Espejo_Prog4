from decimal import Decimal

from sqlalchemy import delete, text
from sqlmodel import Session, select

from app.core.db import create_db_and_tables, engine
from app.core.security import hash_password
from app.models.categoria import Categoria
from app.models.configuracion_empresa import ConfiguracionEmpresa
from app.models.estado_pedido import EstadoPedido
from app.models.ingrediente import Ingrediente
from app.models.producto import Producto
from app.models.producto_categoria import ProductoCategoria
from app.models.producto_ingrediente import ProductoIngrediente
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

PLACEHOLDER_IMAGE = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=900&q=80"

CATEGORIAS_DEMO = [
    {"nombre": "Hamburguesas", "descripcion": "Hamburguesas artesanales y medallones caseros."},
    {"nombre": "Pizzas", "descripcion": "Pizzas clásicas y especiales."},
    {"nombre": "Empanadas", "descripcion": "Empanadas al horno."},
    {"nombre": "Minutas", "descripcion": "Platos rápidos y porciones calientes."},
    {"nombre": "Ensaladas", "descripcion": "Opciones frescas y livianas."},
    {"nombre": "Sándwiches", "descripcion": "Sándwiches y lomitos."},
    {"nombre": "Bebidas", "descripcion": "Bebidas frías."},
    {"nombre": "Postres", "descripcion": "Postres y dulces."},
    {"nombre": "Combos", "descripcion": "Menús armados para presentar el sistema."},
]

INGREDIENTES_DEMO = [
    ("Pan de hamburguesa", "ud", "Pan brioche o clásico para hamburguesas", False, "120"),
    ("Medallón de carne", "ud", "Medallón de carne vacuna", False, "120"),
    ("Medallón vegetariano", "ud", "Medallón de vegetales y legumbres", False, "60"),
    ("Queso cheddar", "g", "Queso cheddar feteado", False, "5000"),
    ("Queso muzzarella", "g", "Muzzarella para pizzas y minutas", False, "12000"),
    ("Queso parmesano", "g", "Queso rallado", False, "2500"),
    ("Lechuga", "g", "Lechuga fresca", False, "4500"),
    ("Tomate", "g", "Tomate fresco", False, "9000"),
    ("Cebolla", "g", "Cebolla blanca", False, "6000"),
    ("Cebolla morada", "g", "Cebolla morada fresca", False, "3500"),
    ("Panceta", "g", "Panceta ahumada", False, "4500"),
    ("Huevo", "ud", "Huevo fresco", True, "80"),
    ("Masa de pizza", "ud", "Pre-pizza o bollo de masa", False, "60"),
    ("Salsa de tomate", "g", "Salsa de tomate casera", False, "9000"),
    ("Jamón cocido", "g", "Jamón cocido feteado", False, "5000"),
    ("Aceitunas", "g", "Aceitunas verdes", False, "2500"),
    ("Morrón", "g", "Morrón rojo", False, "3500"),
    ("Carne cortada a cuchillo", "g", "Relleno de carne para empanadas", False, "9000"),
    ("Pollo", "g", "Pollo cocido o grillado", False, "9000"),
    ("Tapa de empanada", "ud", "Disco de masa para empanada", False, "200"),
    ("Papas", "g", "Papas bastón", False, "18000"),
    ("Milanesa de carne", "ud", "Milanesa de carne rebozada", False, "60"),
    ("Milanesa de pollo", "ud", "Milanesa de pollo rebozada", False, "60"),
    ("Pan de lomo", "ud", "Pan para lomito o sándwich", False, "80"),
    ("Lomo", "g", "Carne de lomo para sándwich", False, "7000"),
    ("Rúcula", "g", "Rúcula fresca", False, "2500"),
    ("Croutons", "g", "Croutons tostados", False, "1800"),
    ("Aderezo Caesar", "ml", "Aderezo para ensalada Caesar", True, "3000"),
    ("Arroz", "g", "Arroz cocido/base", False, "9000"),
    ("Atún", "g", "Atún al natural", True, "3000"),
    ("Agua sin gas", "ud", "Botella de agua 500ml", False, "80"),
    ("Gaseosa cola", "ud", "Lata o botella de gaseosa cola", False, "80"),
    ("Gaseosa lima limón", "ud", "Lata o botella de lima limón", False, "80"),
    ("Jugo de naranja", "ml", "Jugo exprimido o preparado", False, "6000"),
    ("Café", "g", "Café molido", False, "2000"),
    ("Leche", "ml", "Leche para café y postres", True, "6000"),
    ("Brownie", "ud", "Porción de brownie", True, "40"),
    ("Flan", "ud", "Porción de flan casero", True, "40"),
    ("Dulce de leche", "g", "Dulce de leche repostero", True, "4000"),
    ("Helado", "g", "Helado para postres", True, "5000"),
]

PRODUCTOS_DEMO = [
    {
        "nombre": "Hamburguesa Clásica", "categoria": "Hamburguesas", "precio": "5200",
        "descripcion": "Medallón de carne, lechuga, tomate y salsa de la casa.",
        "imagen": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Pan de hamburguesa", "1"), ("Medallón de carne", "1"), ("Lechuga", "30"), ("Tomate", "40")],
    },
    {
        "nombre": "Cheese Burger", "categoria": "Hamburguesas", "precio": "5900",
        "descripcion": "Medallón de carne con cheddar y cebolla caramelizada.",
        "imagen": "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Pan de hamburguesa", "1"), ("Medallón de carne", "1"), ("Queso cheddar", "40"), ("Cebolla", "30")],
    },
    {
        "nombre": "Burger Bacon", "categoria": "Hamburguesas", "precio": "6900",
        "descripcion": "Carne, cheddar, panceta crocante y salsa barbacoa.",
        "imagen": "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Pan de hamburguesa", "1"), ("Medallón de carne", "1"), ("Queso cheddar", "40"), ("Panceta", "50")],
    },
    {
        "nombre": "Doble Cheddar", "categoria": "Hamburguesas", "precio": "7600",
        "descripcion": "Doble medallón, doble cheddar y cebolla.",
        "imagen": "https://images.unsplash.com/photo-1571091718767-18b5b1457add?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Pan de hamburguesa", "1"), ("Medallón de carne", "2"), ("Queso cheddar", "80"), ("Cebolla", "30")],
    },
    {
        "nombre": "Veggie Burger", "categoria": "Hamburguesas", "precio": "6100",
        "descripcion": "Medallón vegetal con tomate, lechuga y cebolla morada.",
        "imagen": "https://images.unsplash.com/photo-1520072959219-c595dc870360?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Pan de hamburguesa", "1"), ("Medallón vegetariano", "1"), ("Lechuga", "35"), ("Tomate", "40"), ("Cebolla morada", "25")],
    },
    {
        "nombre": "Pizza Muzzarella", "categoria": "Pizzas", "precio": "6400",
        "descripcion": "Pizza clásica con salsa de tomate, muzzarella y aceitunas.",
        "imagen": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Masa de pizza", "1"), ("Salsa de tomate", "180"), ("Queso muzzarella", "300"), ("Aceitunas", "30")],
    },
    {
        "nombre": "Pizza Especial", "categoria": "Pizzas", "precio": "7600",
        "descripcion": "Muzzarella, jamón, morrón y aceitunas.",
        "imagen": "https://images.unsplash.com/photo-1594007654729-407eedc4be65?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Masa de pizza", "1"), ("Salsa de tomate", "180"), ("Queso muzzarella", "300"), ("Jamón cocido", "120"), ("Morrón", "60"), ("Aceitunas", "30")],
    },
    {
        "nombre": "Pizza Fugazzeta", "categoria": "Pizzas", "precio": "7200",
        "descripcion": "Muzzarella y mucha cebolla.",
        "imagen": "https://images.unsplash.com/photo-1601924582970-9238bcb495d9?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Masa de pizza", "1"), ("Queso muzzarella", "320"), ("Cebolla", "180")],
    },
    {
        "nombre": "Pizza Rúcula y Parmesano", "categoria": "Pizzas", "precio": "8200",
        "descripcion": "Muzzarella, rúcula fresca y parmesano.",
        "imagen": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Masa de pizza", "1"), ("Salsa de tomate", "160"), ("Queso muzzarella", "280"), ("Rúcula", "50"), ("Queso parmesano", "35")],
    },
    {
        "nombre": "Empanada de Carne", "categoria": "Empanadas", "precio": "900",
        "descripcion": "Empanada de carne suave al horno.",
        "imagen": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Tapa de empanada", "1"), ("Carne cortada a cuchillo", "80"), ("Cebolla", "25"), ("Huevo", "0.25")],
    },
    {
        "nombre": "Empanada de Pollo", "categoria": "Empanadas", "precio": "900",
        "descripcion": "Empanada rellena de pollo condimentado.",
        "imagen": "https://images.unsplash.com/photo-1625944525533-473f1a3d54e7?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Tapa de empanada", "1"), ("Pollo", "85"), ("Cebolla", "25"), ("Morrón", "10")],
    },
    {
        "nombre": "Docena de Empanadas", "categoria": "Empanadas", "precio": "9800",
        "descripcion": "Docena surtida ideal para compartir.",
        "imagen": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Tapa de empanada", "12"), ("Carne cortada a cuchillo", "480"), ("Pollo", "480"), ("Cebolla", "250")],
    },
    {
        "nombre": "Papas Fritas", "categoria": "Minutas", "precio": "3900",
        "descripcion": "Porción grande de papas fritas crocantes.",
        "imagen": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Papas", "500")],
    },
    {
        "nombre": "Papas Cheddar", "categoria": "Minutas", "precio": "5200",
        "descripcion": "Papas fritas con cheddar y panceta.",
        "imagen": "https://images.unsplash.com/photo-1585109649139-366815a0d713?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Papas", "500"), ("Queso cheddar", "120"), ("Panceta", "80")],
    },
    {
        "nombre": "Milanesa con Papas", "categoria": "Minutas", "precio": "7600",
        "descripcion": "Milanesa de carne con guarnición de papas fritas.",
        "imagen": "https://www.clarin.com/img/2025/02/20/dhYFC119u_1256x620__2.jpg",
        "ingredientes": [("Milanesa de carne", "1"), ("Papas", "350")],
    },
    {
        "nombre": "Milanesa Napolitana", "categoria": "Minutas", "precio": "8800",
        "descripcion": "Milanesa con salsa, jamón, muzzarella y papas.",
        "imagen": "https://www.lanacion.com.ar/resizer/v2/milanesa-a-la-napolitana-con-guarnicion-de-papas-VLWFAANIWBGPFO4CSUHS7RYVVQ.jpg?auth=335fda04cf2733e39d11ca0ba979c1d0a8a55e6cdec15e4d5b00cfd59fbf9ed8&width=880&height=586&quality=70&smart=true",
        "ingredientes": [("Milanesa de carne", "1"), ("Salsa de tomate", "90"), ("Jamón cocido", "80"), ("Queso muzzarella", "120"), ("Papas", "300")],
    },
    {
        "nombre": "Ensalada Caesar", "categoria": "Ensaladas", "precio": "6200",
        "descripcion": "Lechuga, pollo, croutons, parmesano y aderezo Caesar.",
        "imagen": "https://images.unsplash.com/photo-1546793665-c74683f339c1?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Lechuga", "130"), ("Pollo", "140"), ("Croutons", "40"), ("Queso parmesano", "25"), ("Aderezo Caesar", "60")],
    },
    {
        "nombre": "Ensalada Tuna", "categoria": "Ensaladas", "precio": "5900",
        "descripcion": "Arroz, atún, tomate, huevo y hojas verdes.",
        "imagen": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Arroz", "160"), ("Atún", "90"), ("Tomate", "70"), ("Huevo", "1"), ("Lechuga", "80")],
    },
    {
        "nombre": "Ensalada Fresca", "categoria": "Ensaladas", "precio": "4700",
        "descripcion": "Lechuga, tomate, cebolla morada y rúcula.",
        "imagen": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Lechuga", "120"), ("Tomate", "90"), ("Cebolla morada", "35"), ("Rúcula", "40")],
    },
    {
        "nombre": "Lomito Completo", "categoria": "Sándwiches", "precio": "7900",
        "descripcion": "Lomo, jamón, queso, huevo, lechuga y tomate.",
        "imagen": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Pan de lomo", "1"), ("Lomo", "180"), ("Jamón cocido", "60"), ("Queso muzzarella", "70"), ("Huevo", "1"), ("Lechuga", "30"), ("Tomate", "40")],
    },
    {
        "nombre": "Sándwich de Milanesa", "categoria": "Sándwiches", "precio": "6900",
        "descripcion": "Milanesa de pollo con lechuga, tomate y queso.",
        "imagen": "https://images.unsplash.com/photo-1553909489-cd47e0907980?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Pan de lomo", "1"), ("Milanesa de pollo", "1"), ("Lechuga", "35"), ("Tomate", "45"), ("Queso muzzarella", "60")],
    },
    {
        "nombre": "Agua Mineral", "categoria": "Bebidas", "precio": "1400",
        "descripcion": "Botella de agua sin gas 500ml.",
        "imagen": "https://images.unsplash.com/photo-1523362628745-0c100150b504?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Agua sin gas", "1")],
    },
    {
        "nombre": "Gaseosa Cola", "categoria": "Bebidas", "precio": "1800",
        "descripcion": "Gaseosa cola fría.",
        "imagen": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Gaseosa cola", "1")],
    },
    {
        "nombre": "Gaseosa Lima Limón", "categoria": "Bebidas", "precio": "1800",
        "descripcion": "Bebida lima limón fría.",
        "imagen": "https://images.unsplash.com/photo-1581636625402-29b2a704ef13?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Gaseosa lima limón", "1")],
    },
    {
        "nombre": "Jugo de Naranja", "categoria": "Bebidas", "precio": "2400",
        "descripcion": "Jugo de naranja fresco.",
        "imagen": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Jugo de naranja", "350")],
    },
    {
        "nombre": "Café con Leche", "categoria": "Bebidas", "precio": "2200",
        "descripcion": "Café con leche caliente.",
        "imagen": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Café", "15"), ("Leche", "180")],
    },
    {
        "nombre": "Brownie", "categoria": "Postres", "precio": "3200",
        "descripcion": "Brownie húmedo con dulce de leche.",
        "imagen": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Brownie", "1"), ("Dulce de leche", "50")],
    },
    {
        "nombre": "Flan con Dulce", "categoria": "Postres", "precio": "2900",
        "descripcion": "Flan casero con dulce de leche.",
        "imagen": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Flan", "1"), ("Dulce de leche", "60")],
    },
    {
        "nombre": "Brownie con Helado", "categoria": "Postres", "precio": "4300",
        "descripcion": "Brownie tibio con bocha de helado.",
        "imagen": "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Brownie", "1"), ("Helado", "120"), ("Dulce de leche", "40")],
    },
    {
        "nombre": "Combo Burger", "categoria": "Combos", "precio": "9200",
        "descripcion": "Hamburguesa clásica con papas y gaseosa cola.",
        "imagen": "https://images.unsplash.com/photo-1610614819513-58e34989848b?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Pan de hamburguesa", "1"), ("Medallón de carne", "1"), ("Lechuga", "30"), ("Tomate", "40"), ("Papas", "300"), ("Gaseosa cola", "1")],
    },
    {
        "nombre": "Combo Pizza", "categoria": "Combos", "precio": "10500",
        "descripcion": "Pizza muzzarella con gaseosa lima limón.",
        "imagen": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=900&q=80",
        "ingredientes": [("Masa de pizza", "1"), ("Salsa de tomate", "180"), ("Queso muzzarella", "300"), ("Aceitunas", "30"), ("Gaseosa lima limón", "1")],
    },
    {
        "nombre": "Combo Milanesa", "categoria": "Combos", "precio": "10800",
        "descripcion": "Milanesa con papas, bebida y postre.",
        "imagen": "https://tb-static.uber.com/prod/image-proc/processed_images/b7b125386322397c0101f08860a8424c/bc9c318a9c96996e2d990faf2b0c65f6.jpeg",
        "ingredientes": [("Milanesa de carne", "1"), ("Papas", "350"), ("Gaseosa cola", "1"), ("Flan", "1")],
    },
]


def _ensure_v7_schema(session: Session) -> None:
    """Agrega columnas v7 cuando se reutiliza una BD ya creada con create_all().

    create_all() crea tablas nuevas, pero no modifica tablas existentes.
    Estas instrucciones hacen segura la actualización local sin borrar datos.
    """
    statements = [
        "ALTER TABLE IF EXISTS producto ADD COLUMN IF NOT EXISTS unidad_venta_id BIGINT",
        "ALTER TABLE IF EXISTS producto ADD COLUMN IF NOT EXISTS margen_ganancia_porcentaje NUMERIC(6,2) NOT NULL DEFAULT 0",
        "ALTER TABLE IF EXISTS ingrediente ADD COLUMN IF NOT EXISTS stock_cantidad NUMERIC(12,3) NOT NULL DEFAULT 0",
        "ALTER TABLE IF EXISTS ingrediente ADD COLUMN IF NOT EXISTS precio_costo_total NUMERIC(12,2) NOT NULL DEFAULT 0",
        "ALTER TABLE IF EXISTS ingrediente ADD COLUMN IF NOT EXISTS precio_costo_unitario NUMERIC(12,4) NOT NULL DEFAULT 0",
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
        "ALTER TABLE IF EXISTS pedido ADD COLUMN IF NOT EXISTS tipo_entrega VARCHAR(20) NOT NULL DEFAULT 'RETIRO'",
        "ALTER TABLE IF EXISTS pedido ADD COLUMN IF NOT EXISTS domicilio_retiro_snap VARCHAR(255)",
        "ALTER TABLE IF EXISTS pedido ADD COLUMN IF NOT EXISTS datos_transferencia_snap VARCHAR(500)",
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



def _get_unidad_por_simbolo(session: Session, simbolo: str) -> UnidadMedida:
    unidad = session.exec(select(UnidadMedida).where(UnidadMedida.simbolo == simbolo)).first()
    if unidad is None:
        raise RuntimeError(f"No existe la unidad de medida {simbolo}. Revisá UNIDADES_MEDIDA.")
    return unidad


def _get_o_crear_categoria(session: Session, nombre: str, descripcion: str | None = None, parent: Categoria | None = None) -> Categoria:
    categoria = session.exec(select(Categoria).where(Categoria.nombre == nombre)).first()
    if categoria is None:
        categoria = Categoria(nombre=nombre)
        session.add(categoria)
        session.flush()
    categoria.descripcion = descripcion
    categoria.parent_id = parent.id if parent else None
    categoria.activo = True
    categoria.deleted_at = None
    session.add(categoria)
    session.flush()
    return categoria


def _get_o_crear_ingrediente(
    session: Session,
    nombre: str,
    unidad: UnidadMedida,
    descripcion: str | None,
    es_alergeno: bool,
    stock: str,
    precio_costo_total: str | None = None,
) -> Ingrediente:
    ingrediente = session.exec(select(Ingrediente).where(Ingrediente.nombre == nombre)).first()
    if ingrediente is None:
        ingrediente = Ingrediente(nombre=nombre)
        session.add(ingrediente)
        session.flush()
    ingrediente.descripcion = descripcion
    ingrediente.es_alergeno = es_alergeno
    ingrediente.stock_cantidad = stock
    if precio_costo_total is None:
        costo_unitario_demo = {"ud": Decimal("500"), "g": Decimal("5"), "kg": Decimal("5000"), "ml": Decimal("3"), "L": Decimal("3000")}.get(unidad.simbolo, Decimal("1"))
        precio_costo_total = str((Decimal(stock) * costo_unitario_demo).quantize(Decimal("0.01")))
    ingrediente.precio_costo_total = precio_costo_total
    stock_decimal = Decimal(stock or "0")
    precio_decimal = Decimal(precio_costo_total or "0")
    ingrediente.precio_costo_unitario = Decimal("0.0000") if stock_decimal <= 0 or precio_decimal <= 0 else (precio_decimal / stock_decimal).quantize(Decimal("0.0001"))
    ingrediente.unidad_medida_id = unidad.id
    ingrediente.activo = True
    ingrediente.deleted_at = None
    session.add(ingrediente)
    session.flush()
    return ingrediente


def _limpiar_relaciones_producto(session: Session, producto_id: int) -> None:
    session.exec(delete(ProductoCategoria).where(ProductoCategoria.producto_id == producto_id))
    session.exec(delete(ProductoIngrediente).where(ProductoIngrediente.producto_id == producto_id))
    session.flush()


def _seed_catalogo_demo(session: Session) -> None:
    """Carga un catálogo amplio para demo/presentación.

    Es idempotente: se puede ejecutar varias veces sin duplicar productos,
    categorías ni ingredientes. Si ya existen, actualiza stock, precios,
    imágenes y recetas para que la demo quede consistente.
    """
    unidades = {simbolo: _get_unidad_por_simbolo(session, simbolo) for _, simbolo, _ in UNIDADES_MEDIDA}

    categorias: dict[str, Categoria] = {}
    for data in CATEGORIAS_DEMO:
        categorias[data["nombre"]] = _get_o_crear_categoria(session, data["nombre"], data["descripcion"])

    ingredientes: dict[str, Ingrediente] = {}
    for nombre, simbolo, descripcion, es_alergeno, stock in INGREDIENTES_DEMO:
        ingredientes[nombre] = _get_o_crear_ingrediente(
            session=session,
            nombre=nombre,
            unidad=unidades[simbolo],
            descripcion=descripcion,
            es_alergeno=es_alergeno,
            stock=stock,
        )

    for data in PRODUCTOS_DEMO:
        producto = session.exec(select(Producto).where(Producto.nombre == data["nombre"])).first()
        if producto is None:
            producto = Producto(nombre=data["nombre"])
            session.add(producto)
            session.flush()

        producto.descripcion = data["descripcion"]
        producto.precio_base = data["precio"]
        producto.margen_ganancia_porcentaje = Decimal("50.00")
        producto.unidad_venta_id = None
        producto.imagenes_url = [data.get("imagen") or PLACEHOLDER_IMAGE]
        producto.disponible = True
        producto.activo = True
        producto.deleted_at = None
        session.add(producto)
        session.flush()

        _limpiar_relaciones_producto(session, producto.id)

        categoria = categorias[data["categoria"]]
        session.add(ProductoCategoria(producto_id=producto.id, categoria_id=categoria.id, es_principal=True))

        for ingrediente_nombre, cantidad in data["ingredientes"]:
            ingrediente = ingredientes[ingrediente_nombre]
            session.add(
                ProductoIngrediente(
                    producto_id=producto.id,
                    ingrediente_id=ingrediente.id,
                    cantidad=cantidad,
                    unidad_medida_id=ingrediente.unidad_medida_id,
                    es_removible=False,
                )
            )
        session.flush()


def _seed_configuracion_empresa(session: Session) -> None:
    config = session.exec(select(ConfiguracionEmpresa)).first()
    if config is None:
        config = ConfiguracionEmpresa()
    config.nombre_empresa = "FoodStore"
    config.domicilio_retiro = "Av. Siempre Viva 742, Mendoza"
    config.banco = "Banco Nación"
    config.titular = "FoodStore SRL"
    config.cuit = "30-12345678-9"
    config.cbu = "0000003100012345678901"
    config.alias = "FOODSTORE.DEMO.MP"
    config.instrucciones_transferencia = "Enviar comprobante al local o mostrarlo al retirar el pedido."
    session.add(config)
    session.flush()


def run_seed() -> None:
    create_db_and_tables()

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

        session.flush()
        _seed_configuracion_empresa(session)
        _seed_catalogo_demo(session)

        session.commit()


if __name__ == "__main__":
    run_seed()
    print("Seed obligatorio ejecutado correctamente.")
    print(f"Usuario admin: {ADMIN_EMAIL}")
    print(f"Contraseña admin: {ADMIN_PASSWORD}")
