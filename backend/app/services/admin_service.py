from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException, status

from app.models.usuario import Usuario
from app.schemas.admin_schema import (
    DashboardEstadoPedido,
    DashboardIngredienteStockBajo,
    DashboardMetricasRead,
    DashboardSerieDiaria,
    DashboardTopProducto,
    DashboardVentaFormaPago,
    UsuarioAdminUpdate,
    UsuarioRolesUpdate,
)
from app.uow.unit_of_work import SQLModelUnitOfWork


ROLES_VALIDOS = {"ADMIN", "STOCK", "PEDIDOS", "CLIENT"}


def listar_usuarios(
    uow: SQLModelUnitOfWork,
    rol: str | None = None,
    search: str | None = None,
    incluir_eliminados: bool = False,
    page: int = 1,
    size: int = 10,
) -> list[Usuario]:
    if rol and rol.upper().strip() not in ROLES_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol inválido. Usá ADMIN, STOCK, PEDIDOS o CLIENT.",
        )

    return uow.usuarios.list_paginated_admin(
        rol_codigo=rol.upper().strip() if rol else None,
        search=search,
        incluir_eliminados=incluir_eliminados,
        page=page,
        size=size,
    )


def obtener_usuario_admin(uow: SQLModelUnitOfWork, usuario_id: int) -> Usuario:
    usuario = uow.usuarios.get_by_id_with_roles(usuario_id)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )
    return usuario


def actualizar_usuario(
    uow: SQLModelUnitOfWork,
    usuario_id: int,
    payload: UsuarioAdminUpdate,
) -> Usuario:
    usuario = obtener_usuario_admin(uow, usuario_id)

    if usuario.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede actualizar un usuario eliminado.",
        )

    if payload.email is not None:
        email = str(payload.email).lower().strip()
        existente = uow.usuarios.get_by_email_any_status(email)
        if existente is not None and existente.id != usuario.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe otro usuario con ese email.",
            )
        usuario.email = email

    if payload.nombre is not None:
        usuario.nombre = payload.nombre.strip()

    if payload.apellido is not None:
        usuario.apellido = payload.apellido.strip() or None

    if payload.activo is not None:
        usuario.activo = payload.activo
        if payload.activo:
            usuario.deleted_at = None

    usuario.updated_at = datetime.now(timezone.utc)
    return uow.usuarios.update(usuario)


def eliminar_usuario(uow: SQLModelUnitOfWork, usuario_id: int, usuario_actual: Usuario) -> Usuario:
    if usuario_actual.id == usuario_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No podés eliminar tu propio usuario administrador.",
        )

    usuario = obtener_usuario_admin(uow, usuario_id)
    if usuario.deleted_at is not None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado o ya eliminado.",
        )

    usuario.activo = False
    usuario.deleted_at = datetime.now(timezone.utc)
    usuario.updated_at = datetime.now(timezone.utc)
    return uow.usuarios.update(usuario)


def asignar_roles(
    uow: SQLModelUnitOfWork,
    usuario_id: int,
    payload: UsuarioRolesUpdate,
    usuario_actual: Usuario,
) -> Usuario:
    usuario = obtener_usuario_admin(uow, usuario_id)

    if usuario.deleted_at is not None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pueden asignar roles a un usuario eliminado o inactivo.",
        )

    roles_normalizados = sorted({codigo.upper().strip() for codigo in payload.roles})
    if not roles_normalizados:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario debe tener al menos un rol.",
        )

    invalidos = [codigo for codigo in roles_normalizados if codigo not in ROLES_VALIDOS]
    if invalidos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Roles inválidos: {', '.join(invalidos)}.",
        )

    if usuario_actual.id == usuario_id and "ADMIN" not in roles_normalizados:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No podés quitarte el rol ADMIN a vos mismo.",
        )

    roles = []
    for codigo in roles_normalizados:
        rol = uow.roles.get_by_codigo(codigo)
        if rol is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"No existe el rol {codigo}. Ejecutá el seed obligatorio.",
            )
        roles.append(rol)

    usuario.roles = roles
    usuario.updated_at = datetime.now(timezone.utc)
    return uow.usuarios.update(usuario)


def activar_usuario(uow: SQLModelUnitOfWork, usuario_id: int) -> Usuario:
    usuario = obtener_usuario_admin(uow, usuario_id)
    usuario.activo = True
    usuario.deleted_at = None
    usuario.updated_at = datetime.now(timezone.utc)
    return uow.usuarios.update(usuario)



def obtener_metricas_dashboard(uow: SQLModelUnitOfWork) -> DashboardMetricasRead:
    """Dashboard administrativo completo con métricas y series para gráficos.

    El service no arma consultas SQL directamente: delega todos los SELECT,
    JOIN y GROUP BY en DashboardRepository a través del UoW.
    """

    estados_venta = ["CONFIRMADO", "EN_PREP", "ENTREGADO"]
    hoy = datetime.now(timezone.utc).date()
    inicio_hoy = datetime.combine(hoy, datetime.min.time(), tzinfo=timezone.utc)
    inicio_7_dias = inicio_hoy - timedelta(days=6)

    metricas = uow.dashboard.obtener_metricas_generales(estados_venta, inicio_hoy)
    pedidos_venta = metricas.pop("pedidos_venta")
    ventas_confirmadas = metricas["ventas_confirmadas"]
    ticket_promedio = (ventas_confirmadas / pedidos_venta).quantize(Decimal("0.01")) if pedidos_venta else Decimal("0.00")

    pedidos_por_estado = [
        DashboardEstadoPedido(estado_codigo=str(estado), total=int(total or 0))
        for estado, total in uow.dashboard.obtener_pedidos_por_estado()
    ]

    ventas_por_forma_pago = [
        DashboardVentaFormaPago(
            forma_pago_codigo=str(forma_pago),
            total_pedidos=int(total_pedidos or 0),
            total_ventas=Decimal(str(total_ventas or 0)),
        )
        for forma_pago, total_pedidos, total_ventas in uow.dashboard.obtener_ventas_por_forma_pago(estados_venta)
    ]

    filas_7_dias = uow.dashboard.obtener_pedidos_ultimos_7_dias(estados_venta, inicio_7_dias)
    datos_por_dia = {
        uow.dashboard._fecha_desde_db(fecha): (int(total or 0), Decimal(str(ventas or 0)))
        for fecha, total, ventas in filas_7_dias
    }
    pedidos_ultimos_7_dias = []
    for offset in range(7):
        fecha = inicio_7_dias.date() + timedelta(days=offset)
        total, ventas = datos_por_dia.get(fecha, (0, Decimal("0.00")))
        pedidos_ultimos_7_dias.append(
            DashboardSerieDiaria(
                fecha=fecha,
                label=fecha.strftime("%d/%m"),
                pedidos=total,
                ventas=ventas,
            )
        )

    top_productos = [
        DashboardTopProducto(
            producto_id=int(producto_id),
            nombre=str(nombre),
            unidades_vendidas=int(unidades or 0),
            total_vendido=Decimal(str(total_vendido or 0)),
        )
        for producto_id, nombre, unidades, total_vendido in uow.dashboard.obtener_top_productos(estados_venta, limit=5)
    ]

    ingredientes_stock_bajo = [
        DashboardIngredienteStockBajo(
            ingrediente_id=int(ingrediente_id),
            nombre=str(nombre),
            stock_cantidad=Decimal(str(stock_cantidad or 0)),
            unidad_simbolo=str(unidad_simbolo) if unidad_simbolo else None,
        )
        for ingrediente_id, nombre, stock_cantidad, unidad_simbolo in uow.dashboard.obtener_ingredientes_stock_bajo(limit=6)
    ]

    return DashboardMetricasRead(
        productos_activos=metricas["productos_activos"],
        ingredientes_activos=metricas["ingredientes_activos"],
        usuarios_activos=metricas["usuarios_activos"],
        pedidos_activos=metricas["pedidos_activos"],
        pedidos_hoy=metricas["pedidos_hoy"],
        pagos_aprobados=metricas["pagos_aprobados"],
        pagos_rechazados=metricas["pagos_rechazados"],
        stock_critico=metricas["stock_critico"],
        ventas_confirmadas=metricas["ventas_confirmadas"],
        ventas_hoy=metricas["ventas_hoy"],
        ticket_promedio=ticket_promedio,
        pedidos_por_estado=pedidos_por_estado,
        ventas_por_forma_pago=ventas_por_forma_pago,
        pedidos_ultimos_7_dias=pedidos_ultimos_7_dias,
        top_productos=top_productos,
        ingredientes_stock_bajo=ingredientes_stock_bajo,
    )
