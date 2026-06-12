from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.detalle_pedido import DetallePedido
from app.models.historial_estado_pedido import HistorialEstadoPedido
from app.models.pedido import Pedido
from app.models.producto_ingrediente import ProductoIngrediente
from app.models.usuario import Usuario
from app.schemas.pedido_schema import PedidoCreate
from app.services.auth_service import roles_codigos
from app.uow.unit_of_work import SQLModelUnitOfWork

ESTADO_INICIAL = "PENDIENTE"
ESTADO_CONFIRMADO = "CONFIRMADO"
ESTADO_EN_PREPARACION = "EN_PREPARACION"
ESTADO_ENTREGADO = "ENTREGADO"
ESTADO_CANCELADO = "CANCELADO"

# TPI v6 / ERD v7: 5 estados.
# En MercadoPago, PENDIENTE -> CONFIRMADO queda reservado al pago aprobado.
# Para EFECTIVO se permite que ADMIN/PEDIDOS confirme manualmente el pedido desde el panel.
TRANSICIONES_OPERADOR = {
    ESTADO_INICIAL: {ESTADO_CONFIRMADO, ESTADO_CANCELADO},
    ESTADO_CONFIRMADO: {ESTADO_EN_PREPARACION, ESTADO_CANCELADO},
    ESTADO_EN_PREPARACION: {ESTADO_ENTREGADO, ESTADO_CANCELADO},
}
TRANSICIONES_CLIENTE_CANCELACION = {ESTADO_INICIAL, ESTADO_CONFIRMADO}
ROLES_GESTION_PEDIDOS = {"ADMIN", "PEDIDOS"}


def _tiene_alguno(usuario: Usuario, roles: set[str]) -> bool:
    return bool(set(roles_codigos(usuario)).intersection(roles))


def _ordenar_historial(pedido: Pedido) -> Pedido:
    pedido.historial_estados = sorted(
        pedido.historial_estados,
        key=lambda item: (item.created_at, item.id or 0),
    )
    return pedido


def _obtener_pedido_visible(uow: SQLModelUnitOfWork, pedido_id: int, usuario: Usuario) -> Pedido:
    pedido = uow.pedidos.get_active_with_details(pedido_id)
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado.")

    if not _tiene_alguno(usuario, ROLES_GESTION_PEDIDOS) and pedido.usuario_id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permisos para ver este pedido.",
        )
    return _ordenar_historial(pedido)


def _validar_estado_existente(uow: SQLModelUnitOfWork, codigo: str) -> None:
    estado = uow.estados_pedido.get_by_codigo(codigo)
    if estado is None or not estado.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El estado {codigo} no existe o no está activo.",
        )


def _registrar_historial(
    uow: SQLModelUnitOfWork,
    pedido_id: int,
    estado_desde: str | None,
    estado_hacia: str,
    usuario_id: int | None,
    motivo: str | None = None,
) -> None:
    historial = HistorialEstadoPedido(
        pedido_id=pedido_id,
        estado_desde=estado_desde,
        estado_hacia=estado_hacia,
        usuario_id=usuario_id,
        motivo=motivo,
    )
    uow.historial_estados.create(historial)


def _ingredientes_a_consumir(uow: SQLModelUnitOfWork, pedido: Pedido) -> dict[int, Decimal]:
    consumos: dict[int, Decimal] = {}
    for detalle in pedido.detalles:
        producto = uow.productos.get_active_with_relations(detalle.producto_id)
        if producto is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El producto {detalle.producto_id} ya no existe o fue eliminado.",
            )

        personalizacion = detalle.personalizacion or {}
        if isinstance(personalizacion, dict):
            removidos = set(personalizacion.get("ingredientes_removidos", []))
        else:
            removidos = set(personalizacion or [])
        configs = uow.productos.list_ingrediente_config(detalle.producto_id)
        if not configs:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El producto {producto.nombre} no tiene receta configurada con ingredientes.",
            )

        for config in configs:
            if config.ingrediente_id in removidos:
                continue
            consumos[config.ingrediente_id] = consumos.get(config.ingrediente_id, Decimal("0.000")) + (
                Decimal(config.cantidad) * Decimal(detalle.cantidad)
            )
    return consumos


def _validar_stock_ingredientes(uow: SQLModelUnitOfWork, pedido: Pedido) -> None:
    consumos = _ingredientes_a_consumir(uow, pedido)
    for ingrediente_id, cantidad_necesaria in consumos.items():
        ingrediente = uow.ingredientes.get_active_by_id(ingrediente_id)
        if ingrediente is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El ingrediente {ingrediente_id} ya no existe.")
        if Decimal(ingrediente.stock_cantidad) < cantidad_necesaria:
            unidad = ingrediente.unidad_medida.simbolo if getattr(ingrediente, "unidad_medida", None) else ""
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Stock insuficiente de {ingrediente.nombre}. "
                    f"Necesario: {cantidad_necesaria} {unidad}. Disponible: {ingrediente.stock_cantidad} {unidad}."
                ).strip(),
            )


def _descontar_stock_confirmacion(uow: SQLModelUnitOfWork, pedido: Pedido) -> None:
    consumos = _ingredientes_a_consumir(uow, pedido)
    for ingrediente_id, cantidad_necesaria in consumos.items():
        ingrediente = uow.ingredientes.get_active_by_id(ingrediente_id)
        if ingrediente is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El ingrediente {ingrediente_id} ya no existe.")
        if Decimal(ingrediente.stock_cantidad) < cantidad_necesaria:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Stock insuficiente de {ingrediente.nombre}.")
        ingrediente.stock_cantidad = Decimal(ingrediente.stock_cantidad) - cantidad_necesaria
        ingrediente.updated_at = datetime.now(timezone.utc)
        uow.ingredientes.update(ingrediente)


def _restaurar_stock_cancelacion(uow: SQLModelUnitOfWork, pedido: Pedido) -> None:
    consumos = _ingredientes_a_consumir(uow, pedido)
    for ingrediente_id, cantidad_a_restaurar in consumos.items():
        ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
        if ingrediente is None:
            continue
        ingrediente.stock_cantidad = Decimal(ingrediente.stock_cantidad) + cantidad_a_restaurar
        ingrediente.updated_at = datetime.now(timezone.utc)
        uow.ingredientes.update(ingrediente)


def listar(
    uow: SQLModelUnitOfWork,
    usuario: Usuario,
    estado_codigo: str | None = None,
    usuario_id: int | None = None,
    page: int = 1,
    size: int = 10,
) -> list[Pedido]:
    if _tiene_alguno(usuario, ROLES_GESTION_PEDIDOS):
        pedidos = uow.pedidos.list_active_all(
            estado_codigo=estado_codigo,
            usuario_id=usuario_id,
            page=page,
            size=size,
        )
    else:
        pedidos = uow.pedidos.list_active_for_user(
            usuario.id,
            estado_codigo=estado_codigo,
            page=page,
            size=size,
        )

    return [_ordenar_historial(pedido) for pedido in pedidos]


def obtener_por_id(uow: SQLModelUnitOfWork, pedido_id: int, usuario: Usuario) -> Pedido:
    return _obtener_pedido_visible(uow, pedido_id, usuario)


def crear_desde_carrito(uow: SQLModelUnitOfWork, usuario: Usuario, payload: PedidoCreate) -> Pedido:
    forma_pago = uow.formas_pago.get_by_codigo(payload.forma_pago_codigo)
    if forma_pago is None or not forma_pago.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La forma de pago indicada no existe o no está activa.",
        )

    if payload.direccion_id is not None:
        direccion = uow.direcciones.get_active_by_id_for_user(payload.direccion_id, usuario.id)
        if direccion is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La dirección indicada no existe o no pertenece al usuario autenticado.",
            )

    _validar_estado_existente(uow, ESTADO_INICIAL)

    producto_ids = [item.producto_id for item in payload.items]
    if len(producto_ids) != len(set(producto_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se permiten productos repetidos en el carrito. Sumá cantidades en un único item.",
        )

    productos_por_id = {}
    subtotal = Decimal("0.00")

    for item in payload.items:
        producto = uow.productos.get_active_with_relations(item.producto_id)
        if producto is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El producto {item.producto_id} no existe o fue eliminado.",
            )
        if not producto.disponible:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El producto {producto.nombre} no está disponible.",
            )
        productos_por_id[item.producto_id] = producto
        subtotal += Decimal(producto.precio_base) * item.cantidad

    total = subtotal - Decimal(payload.descuento) + Decimal(payload.costo_envio)
    if total < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El total del pedido no puede ser negativo.",
        )

    pedido = Pedido(
        usuario_id=usuario.id,
        direccion_id=payload.direccion_id,
        estado_codigo=ESTADO_INICIAL,
        forma_pago_codigo=payload.forma_pago_codigo,
        subtotal=subtotal,
        descuento=payload.descuento,
        costo_envio=payload.costo_envio,
        total=total,
        notas=payload.notas,
    )

    try:
        pedido = uow.pedidos.create(pedido)
        for item in payload.items:
            producto = productos_por_id[item.producto_id]
            precio_unitario = Decimal(producto.precio_base)
            subtotal_item = precio_unitario * item.cantidad

            detalle = DetallePedido(
                pedido_id=pedido.id,
                producto_id=producto.id,
                cantidad=item.cantidad,
                nombre_producto_snap=producto.nombre,
                precio_unitario_snap=precio_unitario,
                subtotal_snap=subtotal_item,
                personalizacion=item.personalizacion,
            )
            uow.detalles_pedido.create(detalle)

        _registrar_historial(
            uow,
            pedido_id=pedido.id,
            estado_desde=None,
            estado_hacia=ESTADO_INICIAL,
            usuario_id=usuario.id,
            motivo="Creación del pedido desde carrito.",
        )
        uow.session.flush()
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear el pedido.",
        ) from exc

    creado = uow.pedidos.get_active_with_details(pedido.id)
    if creado is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Pedido creado, pero no pudo recuperarse.")
    return _ordenar_historial(creado)


def confirmar_por_pago(
    uow: SQLModelUnitOfWork,
    pedido_id: int,
    usuario_id: int | None = None,
    motivo: str | None = "Pago aprobado por MercadoPago.",
) -> Pedido:
    _validar_estado_existente(uow, ESTADO_CONFIRMADO)
    pedido = uow.pedidos.get_active_with_details(pedido_id)
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado.")

    if pedido.estado_codigo == ESTADO_CONFIRMADO:
        return _ordenar_historial(pedido)
    if pedido.estado_codigo != ESTADO_INICIAL:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Solo se puede confirmar un pedido PENDIENTE. Estado actual: {pedido.estado_codigo}.",
        )

    _descontar_stock_confirmacion(uow, pedido)
    pedido.estado_codigo = ESTADO_CONFIRMADO
    pedido.updated_at = datetime.now(timezone.utc)
    uow.pedidos.update(pedido)
    _registrar_historial(
        uow,
        pedido_id=pedido.id,
        estado_desde=ESTADO_INICIAL,
        estado_hacia=ESTADO_CONFIRMADO,
        usuario_id=usuario_id,
        motivo=motivo,
    )
    uow.session.flush()
    actualizado = uow.pedidos.get_active_with_details(pedido.id)
    if actualizado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado.")
    return _ordenar_historial(actualizado)


def avanzar_estado(
    uow: SQLModelUnitOfWork,
    pedido_id: int,
    nuevo_estado_codigo: str,
    usuario: Usuario,
    motivo: str | None = None,
    recuperar_stock: bool = True,
) -> Pedido:
    if not _tiene_alguno(usuario, ROLES_GESTION_PEDIDOS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo ADMIN o PEDIDOS pueden avanzar estados de pedidos.",
        )

    pedido = _obtener_pedido_visible(uow, pedido_id, usuario)
    estado_actual = uow.estados_pedido.get_by_codigo(pedido.estado_codigo)
    nuevo_estado = uow.estados_pedido.get_by_codigo(nuevo_estado_codigo)

    if estado_actual is None or nuevo_estado is None or not nuevo_estado.activo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estado inválido.")

    if estado_actual.es_final:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El pedido está en un estado terminal y no admite más transiciones.",
        )

    permitidos = TRANSICIONES_OPERADOR.get(pedido.estado_codigo, set())
    if nuevo_estado_codigo not in permitidos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Transición no permitida: {pedido.estado_codigo} -> {nuevo_estado_codigo}.",
        )

    if pedido.estado_codigo == ESTADO_INICIAL and nuevo_estado_codigo == ESTADO_CONFIRMADO:
        if pedido.forma_pago_codigo == "MERCADOPAGO":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Los pedidos con MercadoPago solo se confirman automáticamente cuando el pago queda aprobado.",
            )
        _descontar_stock_confirmacion(uow, pedido)

    if pedido.estado_codigo == ESTADO_EN_PREPARACION and nuevo_estado_codigo == ESTADO_CANCELADO:
        if "ADMIN" not in set(roles_codigos(usuario)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo ADMIN puede cancelar pedidos en preparación.",
            )

    estado_anterior = pedido.estado_codigo
    if (
        recuperar_stock
        and nuevo_estado_codigo == ESTADO_CANCELADO
        and estado_anterior in {ESTADO_CONFIRMADO, ESTADO_EN_PREPARACION}
    ):
        _restaurar_stock_cancelacion(uow, pedido)

    pedido.estado_codigo = nuevo_estado_codigo
    pedido.updated_at = datetime.now(timezone.utc)

    try:
        uow.pedidos.update(pedido)
        _registrar_historial(
            uow,
            pedido_id=pedido.id,
            estado_desde=estado_anterior,
            estado_hacia=nuevo_estado_codigo,
            usuario_id=usuario.id,
            motivo=motivo,
        )
        uow.session.flush()
    except IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo avanzar el estado del pedido.") from exc

    actualizado = uow.pedidos.get_active_with_details(pedido.id)
    if actualizado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado.")
    return _ordenar_historial(actualizado)


def cancelar_propio(
    uow: SQLModelUnitOfWork,
    pedido_id: int,
    usuario: Usuario,
    motivo: str | None = None,
) -> Pedido:
    pedido = uow.pedidos.get_active_with_details(pedido_id)
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado.")
    if pedido.usuario_id != usuario.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo podés cancelar tus propios pedidos.")

    estado_actual = uow.estados_pedido.get_by_codigo(pedido.estado_codigo)
    if estado_actual is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estado actual inválido.")
    if estado_actual.es_final:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El pedido ya está en un estado terminal.")
    if pedido.estado_codigo not in TRANSICIONES_CLIENTE_CANCELACION:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El cliente solo puede cancelar pedidos en estado PENDIENTE o CONFIRMADO.",
        )

    estado_anterior = pedido.estado_codigo
    if estado_anterior == ESTADO_CONFIRMADO:
        _restaurar_stock_cancelacion(uow, pedido)

    pedido.estado_codigo = ESTADO_CANCELADO
    pedido.updated_at = datetime.now(timezone.utc)

    try:
        uow.pedidos.update(pedido)
        _registrar_historial(
            uow,
            pedido_id=pedido.id,
            estado_desde=estado_anterior,
            estado_hacia=ESTADO_CANCELADO,
            usuario_id=usuario.id,
            motivo=motivo or "Cancelado por el cliente.",
        )
        uow.session.flush()
    except IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo cancelar el pedido.") from exc

    actualizado = uow.pedidos.get_active_with_details(pedido.id)
    if actualizado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado.")
    return _ordenar_historial(actualizado)
