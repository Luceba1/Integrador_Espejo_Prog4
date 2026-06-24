from app.models.configuracion_empresa import ConfiguracionEmpresa
from app.schemas.empresa_schema import ConfiguracionEmpresaUpdate
from app.uow.unit_of_work import SQLModelUnitOfWork


def obtener_configuracion_empresa(uow: SQLModelUnitOfWork) -> ConfiguracionEmpresa:
    return uow.configuracion_empresa.get_or_create_default()


def actualizar_configuracion_empresa(
    uow: SQLModelUnitOfWork,
    payload: ConfiguracionEmpresaUpdate,
) -> ConfiguracionEmpresa:
    config = uow.configuracion_empresa.get_or_create_default()
    for field, value in payload.model_dump().items():
        setattr(config, field, value.strip() if isinstance(value, str) else value)
    return uow.configuracion_empresa.update(config)
