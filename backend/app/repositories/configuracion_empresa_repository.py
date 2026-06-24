from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models.configuracion_empresa import ConfiguracionEmpresa


class ConfiguracionEmpresaRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_actual(self) -> ConfiguracionEmpresa | None:
        return self.session.exec(select(ConfiguracionEmpresa).order_by(ConfiguracionEmpresa.id)).first()

    def get_or_create_default(self) -> ConfiguracionEmpresa:
        config = self.get_actual()
        if config is not None:
            return config

        config = ConfiguracionEmpresa(
            nombre_empresa="FoodStore",
            domicilio_retiro="Completar domicilio de retiro desde Administración > Empresa.",
            banco="Completar banco",
            titular="Completar titular",
            cuit="Completar CUIT",
            cbu="Completar CBU/CVU",
            alias="Completar alias",
            instrucciones_transferencia="Enviar comprobante una vez realizada la transferencia.",
        )
        self.session.add(config)
        self.session.flush()
        self.session.refresh(config)
        return config

    def update(self, config: ConfiguracionEmpresa) -> ConfiguracionEmpresa:
        config.updated_at = datetime.now(timezone.utc)
        self.session.add(config)
        self.session.flush()
        self.session.refresh(config)
        return config
