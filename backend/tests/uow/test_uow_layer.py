from types import SimpleNamespace

import pytest

from app.uow import unit_of_work
from app.uow.unit_of_work import SQLModelUnitOfWork, get_uow


class FakeSession:
    instances = []

    def __init__(self, engine):
        self.engine = engine
        self.committed = False
        self.rolled_back = False
        self.closed = False
        FakeSession.instances.append(self)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


class FakeRepo:
    def __init__(self, session):
        self.session = session


def _patch_uow_dependencies(monkeypatch):
    FakeSession.instances.clear()
    monkeypatch.setattr(unit_of_work, "Session", FakeSession)
    repo_names = [
        "CategoriaRepository",
        "IngredienteRepository",
        "ProductoRepository",
        "RolRepository",
        "UsuarioRepository",
        "EstadoPedidoRepository",
        "FormaPagoRepository",
        "DireccionRepository",
        "PedidoRepository",
        "DetallePedidoRepository",
        "HistorialEstadoRepository",
        "PagoRepository",
        "UnidadMedidaRepository",
    ]
    for name in repo_names:
        monkeypatch.setattr(unit_of_work, name, FakeRepo)


def test_uow_enter_returns_self_and_creates_repositories(monkeypatch):
    _patch_uow_dependencies(monkeypatch)
    with SQLModelUnitOfWork() as uow:
        assert isinstance(uow.categorias, FakeRepo)
        assert uow.categorias.session is uow.session
        assert isinstance(uow.usuarios, FakeRepo)


def test_uow_exit_commits_when_no_exception(monkeypatch):
    _patch_uow_dependencies(monkeypatch)
    with SQLModelUnitOfWork():
        pass
    session = FakeSession.instances[-1]
    assert session.committed is True
    assert session.rolled_back is False
    assert session.closed is True


def test_uow_exit_rolls_back_when_exception(monkeypatch):
    _patch_uow_dependencies(monkeypatch)
    with pytest.raises(RuntimeError):
        with SQLModelUnitOfWork():
            raise RuntimeError("fallo")
    session = FakeSession.instances[-1]
    assert session.rolled_back is True
    assert session.committed is False
    assert session.closed is True


def test_uow_repositories_share_same_session(monkeypatch):
    _patch_uow_dependencies(monkeypatch)
    with SQLModelUnitOfWork() as uow:
        sessions = {uow.categorias.session, uow.productos.session, uow.pedidos.session, uow.pagos.session}
    assert len(sessions) == 1


def test_get_uow_yields_unit_of_work_and_closes(monkeypatch):
    _patch_uow_dependencies(monkeypatch)
    generator = get_uow()
    uow = next(generator)
    assert isinstance(uow, SQLModelUnitOfWork)
    with pytest.raises(StopIteration):
        next(generator)
    assert FakeSession.instances[-1].closed is True
